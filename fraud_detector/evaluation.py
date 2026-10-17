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
    """Fixed-volume ranking; labels evaluate precision, never choose ranked rows."""
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
        "policy": "batch top-k scores; labels used for evaluation, not ranking",
    }
def rule_score(frame) -> np.ndarray:
    """Frozen hand rule; authored with generator knowledge, not independent."""
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


ALERT_BUDGETS = (0.005, 0.01, 0.05, 0.10)


def compare_baselines(y_val, y_test, val_frame, test_frame, val_ml, test_ml,
                      val_tree=None, test_tree=None) -> dict:
    y_val = np.asarray(y_val, dtype=int)
    y_test = np.asarray(y_test, dtype=int)
    scores = {
        "always_normal": (np.zeros(len(y_val)), np.zeros(len(y_test))),
        "fixed_rules": (rule_score(val_frame), rule_score(test_frame)),
        "ml_calibrated": (np.asarray(val_ml), np.asarray(test_ml)),
    }
    if val_tree is not None and test_tree is not None:
        scores["depth3_tree"] = (np.asarray(val_tree), np.asarray(test_tree))
    comparison = {}
    for name, (validation_scores, test_scores) in scores.items():
        comparison[name] = {
            "ranking": rank_metrics(y_test, test_scores, probability=name not in {"fixed_rules", "always_normal"}),
            "budgets": {},
            "exact_test_top_k": {},
        }
        for budget in ALERT_BUDGETS:
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


def expected_calibration_error(labels, scores, bins: int = 10) -> float:
    """Equal-width ECE; descriptive and sensitive to bin choice."""
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if len(labels) != len(scores) or not len(labels):
        raise ValueError("labels and scores must have matching nonzero lengths")
    groups = np.minimum((scores * bins).astype(int), bins - 1)
    return float(sum(
        np.sum(groups == index) / len(scores)
        * abs(labels[groups == index].mean() - scores[groups == index].mean())
        for index in range(bins) if np.any(groups == index)
    ))
def select_cost_threshold(labels, scores, fp_cost: float, fn_cost: float, max_alert_rate: float = .10) -> dict:
    """Minimize a user-supplied linear cost on validation only, under capacity."""
    if fp_cost < 0 or fn_cost < 0:
        raise ValueError("costs must be nonnegative")
    if not 0 < max_alert_rate <= 1:
        raise ValueError("max_alert_rate must be in (0,1]")
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if (not len(scores) or len(labels) != len(scores) or not np.isfinite(scores).all()
            or not np.isin(labels, [0, 1]).all()):
        raise ValueError("Use nonempty, finite scores and matching binary labels")
    # Group score ties once. Repeated confusion_matrix over every distinct
    # threshold was quadratic on the 284k-row public benchmark.
    order = np.argsort(scores, kind="stable")
    sorted_scores, sorted_labels = scores[order], labels[order]
    unique, starts, counts = np.unique(sorted_scores, return_index=True, return_counts=True)
    positives = np.add.reduceat(sorted_labels, starts)
    alerts = np.cumsum(counts[::-1])[::-1]
    true_positives = np.cumsum(positives[::-1])[::-1]
    total_positives = int(labels.sum())
    above_max = float(np.nextafter(unique[-1], np.inf))
    best_key = (fn_cost * total_positives, 0.0, above_max)
    best_threshold = above_max
    for threshold, alert_count, tp in zip(unique, alerts, true_positives, strict=True):
        if alert_count / len(scores) > max_alert_rate + 1e-12:
            continue
        fp = int(alert_count - tp)
        fn = total_positives - int(tp)
        recall = int(tp) / total_positives if total_positives else 0.0
        key = (fp_cost * fp + fn_cost * fn, -recall, float(threshold))
        if key < best_key:
            best_key = key
            best_threshold = float(threshold)
    result = threshold_metrics(labels, scores, best_threshold)
    return {**result, "estimated_cost": float(best_key[0])}


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
            positives = int(np.asarray(labels)[mask].sum())
            slices[dimension][str(value)] = {
                "rows": int(mask.sum()),
                "positives": positives,
                "fraud_prevalence": float(np.asarray(labels)[mask].mean()),
                **row,
                "recall": row["recall"] if positives >= 30 else None,
                "recall_status": "evaluable" if positives >= 30 else "not evaluable (<30 positives)",
            }
    return {"drift": drift, "slices": slices,
            "limitations": "Synthetic simulation and small subgroup samples; no fairness or production drift claim."}
