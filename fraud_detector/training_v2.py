"""Time-ordered synthetic training, disjoint Platt calibration and honest evaluation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from .evaluation import (
    choose_threshold,
    compare_baselines,
    diagnostic_curves,
    monitoring_summary,
    rank_metrics,
    select_cost_threshold,
    threshold_metrics,
)
from .event_stream import generate_event_stream
from .features import FEATURES

ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "data"
MODEL_PATH = ARTIFACT_DIR / "model.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
VALIDATION_PATH = ARTIFACT_DIR / "validation.npz"
ARTIFACT_VERSION = 4
REVIEW_BUDGET = 0.10
DEFAULT_FP_COST = 1.0
DEFAULT_FN_COST = 10.0


def augment_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["night"] = (result.hour < 5).astype(int)
    result["young_account"] = (result.account_age_days < 90).astype(int)
    result["log_amount"] = np.log1p(result.amount)
    return result


def candidates(seed: int) -> dict[str, Pipeline]:
    categories = ["merchant_category", "channel"]
    numeric = [key for key in FEATURES if key not in categories] + [
        "night",
        "young_account",
        "log_amount",
    ]

    def build(regularization: float) -> Pipeline:
        return Pipeline(
            [
                ("features", FunctionTransformer(augment_features, validate=False)),
                (
                    "preprocess",
                    ColumnTransformer(
                        [
                            (
                                "category",
                                OneHotEncoder(
                                    handle_unknown="ignore", sparse_output=False
                                ),
                                categories,
                            ),
                            ("numeric", StandardScaler(), numeric),
                        ]
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        C=regularization, max_iter=1000, random_state=seed
                    ),
                ),
            ]
        )

    # The transparent logistic family is fixed before validation. Validation
    # chooses regularization; an opaque model is not silently substituted.
    return {"logistic_regression": build(1.0), "logistic_regularized": build(0.25)}


class IdentityCalibrator:
    """Uncalibrated fallback for a single-class calibration slice."""

    def __init__(self) -> None:
        self.coef_ = np.array([[1.0]])
        self.intercept_ = np.array([0.0])

    def predict_proba(self, logits: np.ndarray) -> np.ndarray:
        positive = expit(np.asarray(logits).reshape(-1))
        return np.column_stack((1 - positive, positive))


@dataclass
class CalibratedLogistic:
    """A logistic pipeline followed by a disjoint-data sigmoid (Platt) fit."""

    base: Pipeline
    platt: LogisticRegression | IdentityCalibrator

    def predict_proba(self, frame: pd.DataFrame) -> np.ndarray:
        base_logit = self.base.decision_function(frame).reshape(-1, 1)
        return self.platt.predict_proba(base_logit)


def explain(model: CalibratedLogistic, transaction: dict) -> dict:
    """Exact additive contributions to calibrated *log-odds*, not causality."""
    frame = pd.DataFrame([transaction], columns=FEATURES)
    augmented = model.base.named_steps["features"].transform(frame)
    transformer = model.base.named_steps["preprocess"]
    transformed = transformer.transform(augmented)[0]
    names = transformer.get_feature_names_out()
    base_coef = model.base.named_steps["classifier"].coef_[0]
    calibration_slope = float(model.platt.coef_[0, 0])
    terms = np.asarray(transformed) * base_coef * calibration_slope
    intercept = float(
        model.base.named_steps["classifier"].intercept_[0]
    ) * calibration_slope + float(model.platt.intercept_[0])
    contributions = [
        {
            "feature": str(name),
            "contribution": float(value),
            "direction": "raises"
            if value > 0
            else "lowers"
            if value < 0
            else "neutral",
        }
        for name, value in zip(names, terms, strict=True)
    ]
    return {
        "method": "exact_linear_contributions_to_calibrated_log_odds",
        "intercept": intercept,
        "calibrated_log_odds": float(intercept + terms.sum()),
        "top_reasons": sorted(
            contributions, key=lambda item: abs(item["contribution"]), reverse=True
        )[:5],
        "all_contributions": contributions,
        "limitations": "Linear model attribution, not causality or a real-bank reason code.",
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def train(count: int = 12000, seed: int = 42, output_dir: Path = ARTIFACT_DIR) -> dict:
    development = generate_event_stream(count, seed, start="2026-01-01")
    test_seed = (
        seed + 200003
    )  # New seed fixed before viewing this version's final test.
    test = generate_event_stream(max(500, count // 4), test_seed, start="2026-03-01")
    fit_end, calibration_end = int(0.65 * count), int(0.75 * count)
    fit_data = development.iloc[:fit_end]
    calibration_data = development.iloc[fit_end:calibration_end]
    validation_data = development.iloc[calibration_end:]
    assert fit_data.event_time.max() <= calibration_data.event_time.min()
    assert calibration_data.event_time.max() <= validation_data.event_time.min()
    assert validation_data.event_time.max() < test.event_time.min()
    x_fit, y_fit = fit_data[FEATURES], fit_data.is_fraud.to_numpy(dtype=int)
    x_cal, y_cal = (
        calibration_data[FEATURES],
        calibration_data.is_fraud.to_numpy(dtype=int),
    )
    x_val, y_val = (
        validation_data[FEATURES],
        validation_data.is_fraud.to_numpy(dtype=int),
    )
    x_test, y_test = test[FEATURES], test.is_fraud.to_numpy(dtype=int)

    fitted: dict[str, Pipeline] = {}
    validation_pr_auc = {}
    for name, candidate in candidates(seed).items():
        candidate.fit(x_fit, y_fit)
        fitted[name] = candidate
        validation_pr_auc[name] = float(
            average_precision_score(y_val, candidate.predict_proba(x_val)[:, 1])
        )
    selected_name = max(validation_pr_auc, key=validation_pr_auc.get)
    base = fitted[selected_name]
    cal_logit = base.decision_function(x_cal).reshape(-1, 1)
    if len(np.unique(y_cal)) == 2:
        platt = LogisticRegression(max_iter=1000, random_state=seed)
        platt.fit(cal_logit, y_cal)
    else:
        platt = IdentityCalibrator()
    calibration_method = (
        "disjoint Platt sigmoid"
        if len(np.unique(y_cal)) == 2
        else "identity fallback; single-class calibration slice"
    )
    model = CalibratedLogistic(base, platt)
    validation_score = model.predict_proba(x_val)[:, 1]

    # Everything above and threshold choice is fixed before any test scoring.
    selected = select_cost_threshold(
        y_val, validation_score, DEFAULT_FP_COST, DEFAULT_FN_COST, REVIEW_BUDGET
    )
    threshold = selected["threshold"]
    test_score = model.predict_proba(x_test)[:, 1]
    selected_test = threshold_metrics(y_test, test_score, threshold)
    test_rank = rank_metrics(y_test, test_score)
    comparison = compare_baselines(
        y_val, y_test, x_val, x_test, validation_score, test_score
    )
    raw_rank = rank_metrics(y_test, base.predict_proba(x_test)[:, 1])
    metrics = {
        "artifact_version": ARTIFACT_VERSION,
        "dataset": "synthetic scenario event stream only",
        "seed": seed,
        "test_seed": test_seed,
        "rows": len(development) + len(test),
        "development_rows": len(development),
        "train_rows": len(fit_data),
        "calibration_rows": len(calibration_data),
        "validation_rows": len(validation_data),
        "test_rows": len(test),
        "time_split": {
            "fit_end": str(fit_data.event_time.max()),
            "calibration_start": str(calibration_data.event_time.min()),
            "calibration_end": str(calibration_data.event_time.max()),
            "validation_start": str(validation_data.event_time.min()),
            "validation_end": str(validation_data.event_time.max()),
            "test_start": str(test.event_time.min()),
        },
        "train_fraud_rate": float(y_fit.mean()),
        "calibration_fraud_rate": float(y_cal.mean()),
        "validation_fraud_rate": float(y_val.mean()),
        "test_fraud_rate": float(y_test.mean()),
        "selected_model": selected_name,
        "validation_pr_auc": validation_pr_auc,
        "calibration_method": calibration_method,
        "raw_test_brier": raw_rank["brier"],
        "calibrated_test_brier": test_rank["brier"],
        "review_budget": REVIEW_BUDGET,
        "cost_matrix": {
            "false_positive": DEFAULT_FP_COST,
            "false_negative": DEFAULT_FN_COST,
        },
        "threshold_selection": "minimum validation FP/FN cost subject to 10% validation alert cap",
        "threshold": threshold,
        "validation_at_threshold": selected,
        "test_review_rate": selected_test["alert_rate"],
        "roc_auc": test_rank["roc_auc"],
        "pr_auc": test_rank["pr_auc"],
        "precision": selected_test["precision"],
        "recall": selected_test["recall"],
        "f1": selected_test["f1"],
        "fpr": selected_test["fpr"],
        "brier_score": test_rank["brier"],
        "confusion_matrix": selected_test["confusion_matrix"],
        "comparison": comparison,
        "diagnostic_curves": diagnostic_curves(y_test, test_score),
        "monitoring": monitoring_summary(x_val, x_test, y_test, test_score, threshold),
        "scenario_counts": {
            name: int(value)
            for name, value in development.scenario.value_counts().items()
        },
        "production_ready": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    model_file = output_dir / MODEL_PATH.name
    validation_file = output_dir / VALIDATION_PATH.name
    joblib.dump(model, model_file)
    np.savez_compressed(validation_file, scores=validation_score, labels=y_val)
    metrics["model_sha256"] = file_sha256(model_file)
    metrics["validation_sha256"] = file_sha256(validation_file)
    (output_dir / METRICS_PATH.name).write_text(
        json.dumps(metrics, indent=2, allow_nan=False) + "\n"
    )
    return metrics


def score(model: CalibratedLogistic, transaction: dict) -> float:
    value = model.predict_proba(pd.DataFrame([transaction], columns=FEATURES))[0, 1]
    return float(np.clip(value, 0, 1))


__all__ = [
    "ARTIFACT_DIR",
    "ARTIFACT_VERSION",
    "METRICS_PATH",
    "MODEL_PATH",
    "REVIEW_BUDGET",
    "VALIDATION_PATH",
    "CalibratedLogistic",
    "augment_features",
    "candidates",
    "choose_threshold",
    "explain",
    "file_sha256",
    "score",
    "train",
]
