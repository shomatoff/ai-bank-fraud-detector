"""Opt-in ULB CSV research benchmark; never used by the local application."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .evaluation import (
    ALERT_BUDGETS,
    exact_top_k_metrics,
    rank_metrics,
    select_cost_threshold,
    threshold_metrics,
)

ULB_FEATURES = [f"V{number}" for number in range(1, 29)] + ["Amount"]
ULB_COLUMNS = ["Time", *ULB_FEATURES, "Class"]
MAX_DATASET_BYTES = 250_000_000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_ulb_csv(path: Path, expected_sha256: str) -> pd.DataFrame:
    """Require caller-supplied checksum and exact canonical ULB fields."""
    if len(expected_sha256) != 64 or any(char not in "0123456789abcdef" for char in expected_sha256.lower()):
        raise ValueError("A 64-character expected SHA256 is required")
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_DATASET_BYTES:
        raise ValueError("Dataset file is missing, empty or over 250 MB")
    if sha256_file(path) != expected_sha256.lower():
        raise ValueError("Dataset SHA256 mismatch")
    frame = pd.read_csv(path)
    if list(frame.columns) != ULB_COLUMNS:
        raise ValueError("Expected exact ULB Time,V1..V28,Amount,Class header")
    try:
        frame = frame.apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("Non-numeric ULB field") from exc
    if frame.isna().any().any() or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("Missing or non-finite ULB values")
    if (frame.Time < 0).any() or (frame.Amount < 0).any() or not set(frame.Class).issubset({0, 1}):
        raise ValueError("Invalid time, amount or class")
    return frame


def time_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = frame.sort_values("Time", kind="stable").reset_index(drop=True)
    first, second = int(len(ordered) * .6), int(len(ordered) * .8)
    while first < len(ordered) and ordered.Time.iloc[first] == ordered.Time.iloc[first - 1]:
        first += 1
    while second < len(ordered) and ordered.Time.iloc[second] == ordered.Time.iloc[second - 1]:
        second += 1
    if first == 0 or first >= second or second >= len(ordered):
        raise ValueError("Too few distinct times for chronological split")
    parts = (ordered.iloc[:first], ordered.iloc[first:second], ordered.iloc[second:])
    if any(part.Class.nunique() < 2 for part in parts):
        raise ValueError("Each temporal split must have both classes")
    return parts


def _models(seed: int):
    models = {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=seed)),
        "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=120, random_state=seed),
    }
    try:
        from lightgbm import LGBMClassifier
    except ImportError:
        pass
    else:
        models["lightgbm"] = LGBMClassifier(n_estimators=120, max_depth=4,
                                              learning_rate=.08, random_state=seed,
                                              n_jobs=2, verbosity=-1)
    try:
        from xgboost import XGBClassifier
    except ImportError:
        pass
    else:
        models["xgboost"] = XGBClassifier(n_estimators=120, max_depth=4, learning_rate=.08,
                                             tree_method="hist", random_state=seed, n_jobs=2)
    return models


def _rule_scores(frame: pd.DataFrame) -> np.ndarray:
    """Frozen weak rule on interpretable ULB fields only; no PCA tuning."""
    return (frame.Amount.to_numpy() >= 500).astype(float) + frame.Amount.to_numpy() / 100000


def _explanation(name: str, model, row: pd.DataFrame) -> dict:
    if name == "logistic":
        transformed = model.named_steps["standardscaler"].transform(row)[0]
        coefficients = model.named_steps["logisticregression"].coef_[0]
        values = transformed * coefficients
        method = "linear coefficient × standardized feature; non-causal"
    else:
        try:
            import shap
            raw = shap.TreeExplainer(model).shap_values(row)
            values = np.asarray(raw[-1] if isinstance(raw, list) else raw)[0]
            if values.ndim == 2:
                values = values[:, -1]
        except (ImportError, RuntimeError, ValueError, TypeError) as exc:
            return {"method": "SHAP unavailable", "reason": type(exc).__name__, "not_causal": True}
        method = "Tree SHAP on one test row; non-causal"
    ranked = sorted(zip(ULB_FEATURES, values, strict=True), key=lambda pair: abs(pair[1]), reverse=True)
    return {"method": method, "top_features": [{"feature": key, "contribution": float(value)}
                                              for key, value in ranked[:5]], "not_causal": True}


def benchmark(frame: pd.DataFrame, seed: int = 42) -> dict:
    fit, validation, test = time_split(frame)
    x_fit, x_val, x_test = (part[ULB_FEATURES] for part in (fit, validation, test))
    y_fit, y_val, y_test = (part.Class.to_numpy(dtype=int) for part in (fit, validation, test))
    models = _models(seed)
    validation_quality = {}
    output = {}
    for name, model in models.items():
        model.fit(x_fit, y_fit)
        val_scores = model.predict_proba(x_val)[:, 1]
        validation_quality[name] = float(average_precision_score(y_val, val_scores))
        chosen_threshold = select_cost_threshold(y_val, val_scores, 1, 10, .10)["threshold"]
        test_scores = model.predict_proba(x_test)[:, 1]
        output[name] = {
            "test_ranking": rank_metrics(y_test, test_scores),
            "validation_selected_threshold": chosen_threshold,
            "test_at_validation_threshold": threshold_metrics(y_test, test_scores, chosen_threshold),
            "exact_top_k": {str(budget): exact_top_k_metrics(y_test, test_scores, budget)
                            for budget in ALERT_BUDGETS},
            "one_test_row_explanation": _explanation(name, model, x_test.iloc[[0]]),
        }
    rules = _rule_scores(test)
    output["fixed_amount_rule"] = {"test_ranking": rank_metrics(y_test, rules, probability=False),
                                    "exact_top_k": {str(budget): exact_top_k_metrics(y_test, rules, budget)
                                                    for budget in ALERT_BUDGETS}}
    output["always_normal"] = {"alerts": 0, "recall": 0, "precision": 0,
                                "pr_auc": float(y_test.mean()), "cannot_fill_budget": True}
    selected = max(validation_quality, key=validation_quality.get)
    # Idealized analyst feedback: only the first half of chronological validation
    # labels may be confirmed. Later validation labels remain for policy selection.
    feedback_end = len(validation) // 2
    feedback = validation.iloc[:feedback_end]
    policy = validation.iloc[feedback_end:]
    feedback_result = {"status": "not evaluable"}
    if feedback.Class.nunique() == 2 and policy.Class.nunique() == 2:
        before = _models(seed)[selected].fit(x_fit, y_fit)
        after = _models(seed)[selected].fit(
            pd.concat([x_fit, feedback[ULB_FEATURES]]),
            np.r_[y_fit, feedback.Class.to_numpy(dtype=int)],
        )
        feedback_result = {"status": "simulated perfect analyst confirmations, not real feedback",
                           "confirmed_validation_rows": len(feedback), "selected_model": selected,
                           "before": {}, "after": {}}
        for label, fitted in (("before", before), ("after", after)):
            p_val = fitted.predict_proba(policy[ULB_FEATURES])[:, 1]
            threshold = select_cost_threshold(policy.Class, p_val, 1, 10, .10)["threshold"]
            p_test = fitted.predict_proba(x_test)[:, 1]
            feedback_result[label] = {"test_pr_auc": float(average_precision_score(y_test, p_test)),
                                      "test_exact_5pct": exact_top_k_metrics(y_test, p_test, .05),
                                      "test_at_validation_threshold": threshold_metrics(y_test, p_test, threshold)}
    return {"dataset": "caller-provided ULB-compatible CSV; dataset not bundled",
            "seed": seed, "split": {"fit": len(fit), "validation": len(validation), "test": len(test),
                                   "time_fit_max": float(fit.Time.max()), "time_test_min": float(test.Time.min()),
                                   "test_fraud_count": int(y_test.sum())},
            "validation_pr_auc": validation_quality, "selected_on_validation": selected,
            "models": output, "feedback_demo": feedback_result,
            "limits": "Public anonymized benchmark is not a live bank validation; exact top-k needs whole test batch."}
