"""Pure evaluation helpers; all threshold selection uses validation labels."""
from __future__ import annotations

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)


def choose_threshold(scores: np.ndarray, review_budget: float) -> float:
    if not 0 < review_budget < 1:
        raise ValueError("review_budget must be between zero and one")
    # A strict cut over a quantile avoids exceeding capacity on validation ties.
    return float(np.nextafter(np.quantile(scores, 1 - review_budget), np.inf))


def threshold_metrics(labels: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    predicted = scores >= threshold
    tn, fp, fn, tp = confusion_matrix(labels, predicted, labels=[0, 1]).ravel()
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "threshold": float(threshold) if np.isfinite(threshold) else None,
        "alerts": int(predicted.sum()),
        "alert_rate": float(predicted.mean()),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(2 * precision * recall / (precision + recall)) if precision + recall else 0.0,
        "fpr": float(fpr),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def rank_metrics(labels: np.ndarray, scores: np.ndarray, probability: bool = True) -> dict:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    return {
        "pr_auc": float(average_precision_score(labels, scores)),
        "roc_auc": float(roc_auc_score(labels, scores)),
        "brier": float(brier_score_loss(labels, scores)) if probability else None,
    }


def exact_top_k_metrics(labels: np.ndarray, scores: np.ndarray, budget: float) -> dict:
    """Retrospective fixed-volume ranking; uses test scores, never test labels to rank."""
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    k = round(len(scores) * budget)
    chosen = np.argsort(-scores, kind="stable")[:k]
    predicted = np.zeros(len(scores), dtype=bool)
    predicted[chosen] = True
    tn, fp, fn, tp = confusion_matrix(labels, predicted, labels=[0, 1]).ravel()
    precision = tp / k if k else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "alerts": k, "alert_rate": k / len(scores),
        "precision": float(precision), "recall": float(recall),
        "f1": float(2 * precision * recall / (precision + recall)) if precision + recall else 0.0,
        "fpr": float(fpr),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "policy": "retrospective top-k test scores; labels not used for ranking",
    }
def rule_score(frame) -> np.ndarray:
    """A frozen, inspectable baseline: no labels or learned parameters."""
    return (
        2.0 * frame.is_new_device.astype(float)
        + 1.5 * (frame.velocity_1h >= 3).astype(float)
        + 1.5 * (frame.prior_declines_24h >= 1).astype(float)
        + 1.5 * (frame.channel == "transfer").astype(float)
        + 1.0 * (frame.amount >= 1200).astype(float)
        + 1.0 * (frame.account_age_days < 90).astype(float)
        + 0.5 * (frame.country_risk >= 1).astype(float)
        + np.minimum(frame.amount.to_numpy(dtype=float) / 100000, 0.1)
    ).to_numpy(dtype=float)


def compare_baselines(y_val, y_test, val_frame, test_frame, val_ml, test_ml) -> dict:
    y_val = np.asarray(y_val, dtype=int)
    y_test = np.asarray(y_test, dtype=int)
    scores = {
        "always_normal": (np.zeros(len(y_val)), np.zeros(len(y_test))),
        "fixed_rules": (rule_score(val_frame), rule_score(test_frame)),
        "ml_calibrated": (np.asarray(val_ml), np.asarray(test_ml)),
    }
    comparison = {}
    for name, (validation_scores, test_scores) in scores.items():
        comparison[name] = {
            "ranking": rank_metrics(y_test, test_scores, probability=name != "fixed_rules"),
            "budgets": {},
            "exact_test_top_k": {},
        }
        for budget in (0.05, 0.10):
            # Validation-derived threshold: deployable policy, but actual test
            # alert rate may differ from the configured capacity.
            threshold = float("inf") if name == "always_normal" else choose_threshold(validation_scores, budget)
            comparison[name]["budgets"][str(budget)] = threshold_metrics(
                y_test, test_scores, threshold
            )
            # Retrospective same-volume comparison. It is not a deployable
            # threshold, because it needs the entire unlabeled test score batch.
            comparison[name]["exact_test_top_k"][str(budget)] = (
                threshold_metrics(y_test, test_scores, float("inf"))
                if name == "always_normal"
                else exact_top_k_metrics(y_test, test_scores, budget)
            )
    return comparison
def select_cost_threshold(labels, scores, fp_cost: float, fn_cost: float, max_alert_rate: float = .10) -> dict:
    """Minimize a user-supplied linear cost on validation only, under capacity."""
    if fp_cost < 0 or fn_cost < 0:
        raise ValueError("costs must be nonnegative")
    if not 0 < max_alert_rate <= 1:
        raise ValueError("max_alert_rate must be in (0,1]")
    scores = np.asarray(scores, dtype=float)
    candidates = np.r_[np.nextafter(scores.max(), np.inf), np.unique(scores)]
    best = None
    for threshold in candidates:
        result = threshold_metrics(labels, scores, threshold)
        if result["alert_rate"] > max_alert_rate + 1e-12:
            continue
        matrix = result["confusion_matrix"]
        cost = fp_cost * matrix["fp"] + fn_cost * matrix["fn"]
        if best is None or (cost, -result["recall"], threshold) < (
            best["estimated_cost"], -best["recall"], best["threshold"]
        ):
            best = {**result, "estimated_cost": float(cost)}
    assert best is not None
    return best


def diagnostic_curves(labels, scores) -> dict:
    """Downsampled plotting arrays from a final synthetic test, for display only."""
    precision, recall, _pr_threshold = precision_recall_curve(labels, scores)
    fpr, tpr, _roc_threshold = roc_curve(labels, scores)
    observed, predicted = calibration_curve(labels, scores, n_bins=10, strategy="quantile")

    def sampled(*arrays):
        indices = np.unique(np.linspace(0, len(arrays[0]) - 1, min(101, len(arrays[0]))).astype(int))
        return [[float(a[i]) for i in indices] for a in arrays]

    pr_p, pr_r = sampled(precision, recall)
    roc_fpr, roc_tpr = sampled(fpr, tpr)
    return {
        "precision_recall": {"precision": pr_p, "recall": pr_r},
        "roc": {"fpr": roc_fpr, "tpr": roc_tpr},
        "reliability": {
            "predicted": [float(x) for x in predicted],
            "observed": [float(x) for x in observed],
        },
        "notes": "Final synthetic-test diagnostics; not used to select the model or threshold.",
    }


def population_stability_index(reference, observed, bins: int = 10) -> float:
    """PSI with reference quantile bins; descriptive, not a universal alarm."""
    reference = np.asarray(reference, dtype=float)
    observed = np.asarray(observed, dtype=float)
    edges = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    a, _ = np.histogram(reference, bins=edges)
    b, _ = np.histogram(observed, bins=edges)
    a = np.clip(a / len(reference), 1e-6, 1)
    b = np.clip(b / len(observed), 1e-6, 1)
    return float(np.sum((b - a) * np.log(b / a)))


def monitoring_summary(validation_frame, test_frame, labels, scores, threshold) -> dict:
    """Synthetic drift simulation and test slices; never feeds model selection."""
    amount_val = validation_frame.amount.to_numpy(dtype=float)
    amount_test = test_frame.amount.to_numpy(dtype=float)
    drift = {
        "amount_validation_vs_test_psi": population_stability_index(amount_val, amount_test),
        "amount_shifted_1_5x_psi": population_stability_index(amount_val, amount_test * 1.5),
        "simulation": "Multiply independent synthetic test amounts by 1.5; no model retraining.",
    }
    slices = {}
    dimensions = {
        "channel": test_frame.channel.astype(str),
        "country_risk": test_frame.country_risk.astype(str),
        "account_age": np.where(test_frame.account_age_days < 90, "under_90_days", "90_days_or_more"),
    }
    for dimension, values in dimensions.items():
        slices[dimension] = {}
        for value in sorted(set(values)):
            mask = np.asarray(values == value)
            if mask.sum() < 20:
                continue
            row = threshold_metrics(np.asarray(labels)[mask], np.asarray(scores)[mask], threshold)
            slices[dimension][str(value)] = {
                "rows": int(mask.sum()),
                "fraud_prevalence": float(np.asarray(labels)[mask].mean()),
                **row,
            }
    return {"drift": drift, "slices": slices,
            "limitations": "Synthetic simulation and small subgroup samples; no fairness or production drift claim."}
