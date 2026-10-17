"""Reject a challenger that loses important unseen synthetic fraud typologies.

This is a promotion validation gate, not an untouched final performance test.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sklearn.metrics import average_precision_score

from fraud_detector.evaluation import select_cost_threshold, threshold_metrics
from fraud_detector.event_stream import generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training_v2 import candidates, interaction_candidate

FRAUD_TYPES = (
    "account_takeover", "card_testing", "mule_cashout", "new_account_transfer"
)
MAX_RECALL_DROP = 0.05
MIN_HELDOUT_RECALL = 0.20


def promotion_decision(rows: dict[str, dict], tolerance: float = MAX_RECALL_DROP,
                       minimum_recall: float = MIN_HELDOUT_RECALL) -> dict:
    if not rows or not all(math.isfinite(value) and 0 <= value <= 1
                           for value in (tolerance, minimum_recall)):
        raise ValueError("Gate requires typologies and finite limits in [0,1]")
    for name, values in rows.items():
        for field in ("baseline_recall", "challenger_recall"):
            value = values.get(field)
            if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name}: {field} must be finite and in [0,1]")
    regression_failures = [name for name, values in rows.items()
                           if values["challenger_recall"] < values["baseline_recall"] - tolerance]
    coverage_failures = [name for name, values in rows.items()
                         if values["challenger_recall"] < minimum_recall]
    failures = list(dict.fromkeys([*regression_failures, *coverage_failures]))
    return {
        "promote": not failures,
        "failed_typologies": failures,
        "regression_failures": regression_failures,
        "minimum_recall_failures": coverage_failures,
        "maximum_allowed_absolute_recall_drop": tolerance,
        "minimum_required_heldout_recall": minimum_recall,
        "meaning": "Synthetic holdout safety screen only; passing is not bank validation.",
    }


def evaluate(seed: int = 342, count: int = 12000, test_rows: int = 30000) -> dict:
    development = generate_event_stream(count, seed, start="2026-01-01")
    test = generate_event_stream(test_rows, seed + 900003, start="2026-05-01")
    fit = development.iloc[:int(.6 * count)]
    validation = development.iloc[int(.8 * count):]
    rows = {}
    for typology in FRAUD_TYPES:
        known_fit = fit.loc[fit.scenario != typology]
        known_val = validation.loc[validation.scenario != typology]
        held = test.loc[test.scenario == typology]
        if int(held.is_fraud.sum()) < 200:
            raise ValueError(f"{typology} requires at least 200 positive held-out rows")
        baseline_family = candidates(seed)
        for model in baseline_family.values():
            model.fit(known_fit[FEATURES], known_fit.is_fraud)
        baseline_name = max(baseline_family, key=lambda name: average_precision_score(
            known_val.is_fraud,
            baseline_family[name].predict_proba(known_val[FEATURES])[:, 1],
        ))
        models = {
            "baseline": baseline_family[baseline_name],
            "challenger": interaction_candidate(seed).fit(known_fit[FEATURES], known_fit.is_fraud),
        }
        results = {}
        for name, model in models.items():
            val_scores = model.predict_proba(known_val[FEATURES])[:, 1]
            threshold = select_cost_threshold(known_val.is_fraud.to_numpy(), val_scores,
                                              1, 10, .10)["threshold"]
            scores = model.predict_proba(held[FEATURES])[:, 1]
            results[name] = threshold_metrics(held.is_fraud.to_numpy(), scores, threshold)
        rows[typology] = {
            "heldout_rows": len(held), "positives": int(held.is_fraud.sum()),
            "baseline_model": baseline_name,
            "baseline_recall": results["baseline"]["recall"],
            "challenger_recall": results["challenger"]["recall"],
            "baseline_alerts": results["baseline"]["alerts"],
            "challenger_alerts": results["challenger"]["alerts"],
        }
    return {
        "seed": seed, "test_seed": seed + 900003,
        "protocol": "Remove each typology from fit/validation; thresholds from known validation only.",
        "typologies": rows, "decision": promotion_decision(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=342)
    parser.add_argument("--output", type=Path, default=Path("data/heldout_promotion_gate.json"))
    args = parser.parse_args()
    result = evaluate(seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
