"""Opt-in synthetic cohort/time audit; never promotes or saves a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

from fraud_detector.evaluation import (
    exact_top_k_metrics,
    select_cost_threshold,
    threshold_metrics,
)
from fraud_detector.event_stream import generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.generalization import (
    customer_temporal_split,
    customer_top_k_metrics,
)
from fraud_detector.training_v2 import candidates

FRAUD_TYPES = ("account_takeover", "card_testing", "mule_cashout", "new_account_transfer")
HARD_LEGITIMATE = ("legit_travel", "legit_large_purchase", "legit_many_declines")


def evaluate(seed: int = 842, rows: int = 30000) -> dict:
    if rows < 5000:
        raise ValueError("At least 5000 rows required for this descriptive audit")
    parts = customer_temporal_split(generate_event_stream(rows, seed), seed=seed)
    fit, validation = parts["fit"], parts["validation"]
    family = candidates(seed)
    quality = {}
    for name, model in family.items():
        model.fit(fit[FEATURES], fit.is_fraud)
        quality[name] = float(average_precision_score(
            validation.is_fraud, model.predict_proba(validation[FEATURES])[:, 1]
        ))
    selected = max(quality, key=quality.get)
    model = family[selected]
    validation_scores = model.predict_proba(validation[FEATURES])[:, 1]
    threshold = select_cost_threshold(validation.is_fraud.to_numpy(), validation_scores,
                                      1, 10, .10)["threshold"]
    output = {}
    for cohort in ("seen_test", "new_customer_test"):
        part = parts[cohort]
        labels = part.is_fraud.to_numpy()
        scores = model.predict_proba(part[FEATURES])[:, 1]
        flagged = scores >= threshold
        scenarios = {}
        for scenario in FRAUD_TYPES:
            selected_rows = (part.scenario == scenario).to_numpy() & (labels == 1)
            positives = int(selected_rows.sum())
            scenarios[scenario] = {
                "positive_rows": positives,
                "detected": int(flagged[selected_rows].sum()),
                "recall": float(flagged[selected_rows].mean()) if positives >= 30 else None,
                "interpretation": "insufficient positives" if positives < 30 else "synthetic only",
            }
        hard_negative = {}
        for scenario in HARD_LEGITIMATE:
            selected_rows = (part.scenario == scenario).to_numpy() & (labels == 0)
            negatives = int(selected_rows.sum())
            hard_negative[scenario] = {
                "negative_rows": negatives, "false_alerts": int(flagged[selected_rows].sum()),
                "false_alert_rate": float(flagged[selected_rows].mean()) if negatives >= 30 else None,
                "interpretation": "insufficient negatives" if negatives < 30 else "synthetic only",
            }
        output[cohort] = {
            "rows": len(part), "positive_rows": int(labels.sum()),
            "distinct_customers": int(part.customer_id.nunique()),
            "pr_auc": float(average_precision_score(labels, scores)),
            "validation_threshold": threshold_metrics(labels, scores, threshold),
            "retrospective_transaction_top_5pct": exact_top_k_metrics(labels, scores, .05),
            "retrospective_customer_top_5pct": customer_top_k_metrics(
                labels, scores, part.customer_id.to_numpy(), .05
            ),
            "fraud_typologies": scenarios,
            "hard_legitimate": hard_negative,
        }
    assert not (set(fit.customer_id) | set(validation.customer_id)) & set(parts["new_customer_test"].customer_id)
    assert np.isfinite(list(quality.values())).all()
    return {
        "seed": seed, "synthetic_rows": rows,
        "selection": "model PR-AUC and threshold from known-customer validation only",
        "fit_rows": len(fit), "validation_rows": len(validation),
        "validation_pr_auc": quality, "selected_model": selected,
        "customer_cohort_fraction": .20,
        "cohorts": output,
        "limitations": [
            "Synthetic generator and customer IDs only; not real or bank performance.",
            "Known and held-out customers share generator rules; not independent institutions.",
            "Exactly one seed and time window; no confidence interval or deployment decision.",
            "Synthetic labels are immediately known here; real delayed-label embargo is not simulated.",
            "Customer top-k is retrospective; a real queue needs streaming policy and identity governance.",
        ],
        "active_model_changed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=842)
    parser.add_argument("--rows", type=int, default=30000)
    parser.add_argument("--output", type=Path, default=Path("data/generalization_audit.json"))
    args = parser.parse_args()
    result = evaluate(args.seed, args.rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
