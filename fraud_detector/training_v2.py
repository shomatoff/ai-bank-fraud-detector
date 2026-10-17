"""Time-ordered synthetic training, disjoint Platt calibration and honest evaluation."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
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
from sklearn.tree import DecisionTreeClassifier

from .evaluation import (
    choose_threshold,
    compare_baselines,
    diagnostic_curves,
    expected_calibration_error,
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
ARTIFACT_VERSION = 6
SIGNING_KEY_NAME = "artifact-signing.key"
REVIEW_BUDGET = 0.10
DEFAULT_FP_COST = 1.0
DEFAULT_FN_COST = 10.0


def augment_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["night"] = (result.hour < 5).astype(int)
    result["young_account"] = (result.account_age_days < 90).astype(int)
    result["log_amount"] = np.log1p(result.amount)
    return result


def augment_interaction_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Past/current-event interactions; no scenario, label or future inputs."""
    result = augment_features(frame)
    small = (result.amount < 30).astype(int)
    result["small_online_new_device"] = (
        small * (result.channel == "online").astype(int) * result.is_new_device.astype(int)
    )
    result["small_amount_velocity"] = small * result.velocity_1h.clip(upper=10)
    result["new_device_velocity"] = result.is_new_device.astype(int) * result.velocity_1h.clip(upper=10)
    result["young_account_transfer"] = (
        result.young_account * (result.channel == "transfer").astype(int)
    )
    return result


def interaction_candidate(seed: int) -> Pipeline:
    """Interpretable logistic challenger; excluded from deployed candidate selection."""
    categories = ["merchant_category", "channel"]
    numeric = [key for key in FEATURES if key not in categories] + [
        "night", "young_account", "log_amount", "small_online_new_device",
        "small_amount_velocity", "new_device_velocity", "young_account_transfer",
    ]
    return Pipeline([
        ("features", FunctionTransformer(augment_interaction_features, validate=False)),
        ("preprocess", ColumnTransformer([
            ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categories),
            ("numeric", StandardScaler(), numeric),
        ])),
        ("classifier", LogisticRegression(C=0.25, max_iter=1000, random_state=seed)),
    ])


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


def simple_tree(seed: int) -> Pipeline:
    """A learned, deliberately shallow baseline fit on the same fit window."""
    prototype = candidates(seed)["logistic_regression"]
    return Pipeline([
        ("features", prototype.named_steps["features"]),
        ("preprocess", prototype.named_steps["preprocess"]),
        ("classifier", DecisionTreeClassifier(max_depth=3, min_samples_leaf=40,
                                                random_state=seed)),
    ])


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
    """Exact additive contributions to selected-model log-odds, not causality."""
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
        "method": "exact_linear_contributions_to_selected_log_odds",
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


def artifact_signature(key: bytes, model_hash: str, validation_hash: str) -> str:
    payload = f"v{ARTIFACT_VERSION}:{model_hash}:{validation_hash}".encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def signing_key_path() -> Path:
    """Local owner-only key, outside the data/artifact directory."""
    value = os.environ.get("SENTINELAI_HMAC_KEY_FILE")
    return Path(value).expanduser() if value else Path.home() / ".local/share/sentinelai/artifact-signing.key"


def signing_key(output_dir: Path) -> bytes:
    path = signing_key_path().resolve()
    if path.is_relative_to(output_dir.resolve()) or path.is_relative_to(ARTIFACT_DIR.resolve()):
        raise RuntimeError("HMAC key must be outside the artifact/data directory")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.exists():
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(descriptor, "wb") as key_file:
                key_file.write(secrets.token_bytes(32))
    if path.stat().st_mode & 0o077:
        raise RuntimeError("HMAC key file must be owner-only (0600)")
    key = path.read_bytes()
    if len(key) < 32:
        raise RuntimeError("HMAC key must contain at least 32 random bytes")
    return key


def train(count: int = 12000, seed: int = 42, output_dir: Path = ARTIFACT_DIR,
          force_no_calibration: bool = False) -> dict:
    development = generate_event_stream(count, seed, start="2026-01-01")
    test_seed = (
        seed + 400003
    )  # New seed fixed before viewing this version's final test.
    test = generate_event_stream(max(500, count // 4), test_seed, start="2026-03-01")
    fit_end, calibration_end = int(0.60 * count), int(0.80 * count)
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
    candidate_model = CalibratedLogistic(base, platt)
    raw_validation = base.predict_proba(x_val)[:, 1]
    calibrated_validation = candidate_model.predict_proba(x_val)[:, 1]
    calibration_check = {
        "raw_validation_brier": rank_metrics(y_val, raw_validation)["brier"],
        "platt_validation_brier": rank_metrics(y_val, calibrated_validation)["brier"],
        "raw_validation_ece": expected_calibration_error(y_val, raw_validation),
        "platt_validation_ece": expected_calibration_error(y_val, calibrated_validation),
    }
    calibration_enabled = not force_no_calibration and (
        len(np.unique(y_cal)) == 2
        and calibration_check["platt_validation_brier"] < calibration_check["raw_validation_brier"]
        and calibration_check["platt_validation_ece"] < calibration_check["raw_validation_ece"]
    )
    model = candidate_model if calibration_enabled else CalibratedLogistic(base, IdentityCalibrator())
    calibration_method = ("forced off for comparable seed audit" if force_no_calibration
                          else "disjoint Platt sigmoid" if calibration_enabled
                          else "disabled: validation Brier and ECE did not both improve")
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
        y_val, y_test, x_val, x_test, validation_score, test_score,
        *tree_baseline_scores(seed, x_fit, y_fit, x_val, x_test),
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
        "calibration_forced_off": force_no_calibration,
        "calibration_validation_check": calibration_check,
        "raw_test_brier": raw_rank["brier"],
        "selected_test_brier": test_rank["brier"],
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
    metrics["artifact_hmac_sha256"] = artifact_signature(
        signing_key(output_dir), metrics["model_sha256"], metrics["validation_sha256"]
    )
    (output_dir / METRICS_PATH.name).write_text(
        json.dumps(metrics, indent=2, allow_nan=False) + "\n"
    )
    return metrics


def tree_baseline_scores(seed: int, x_fit, y_fit, x_val, x_test) -> tuple[np.ndarray, np.ndarray]:
    tree = simple_tree(seed)
    tree.fit(x_fit, y_fit)
    return tree.predict_proba(x_val)[:, 1], tree.predict_proba(x_test)[:, 1]


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
