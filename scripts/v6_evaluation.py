"""Ten-seed synthetic audit; test scores are descriptive, never used for tuning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from sklearn.metrics import average_precision_score

from fraud_detector.evaluation import (
    ALERT_BUDGETS,
    select_cost_threshold,
    threshold_metrics,
)
from fraud_detector.event_stream import SCENARIOS, generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training import train
from fraud_detector.training_v2 import candidates
from scripts.v5_evaluation import bootstrap_interval

FRAUD_TYPES = ("account_takeover", "card_testing", "mule_cashout", "new_account_transfer")
MODELS = ("fixed_rules", "depth3_tree", "ml_calibrated")
METRICS = ("precision", "recall", "f1", "fpr")


def summarize(rows: list[dict], key: str) -> dict:
    return bootstrap_interval([row[key] for row in rows])


def held_out_typologies(seed: int = 42, count: int = 12000,
                        test_rows: int = 30000) -> dict:
    development = generate_event_stream(count, seed)
    dedicated_test = generate_event_stream(test_rows, seed + 900003, start="2026-05-01")
    fit = development.iloc[:int(.6 * count)]
    validation = development.iloc[int(.8 * count):]
    result = {}
    for name in FRAUD_TYPES:
        fit_known = fit.loc[fit.scenario != name]
        validation_known = validation.loc[validation.scenario != name]
        winner = None
        for candidate_name, candidate in candidates(seed).items():
            candidate.fit(fit_known[FEATURES], fit_known.is_fraud)
            val_scores = candidate.predict_proba(validation_known[FEATURES])[:, 1]
            quality = average_precision_score(validation_known.is_fraud, val_scores)
            if winner is None or quality > winner[0]:
                winner = (quality, candidate_name, candidate, val_scores)
        assert winner is not None
        threshold = select_cost_threshold(
            validation_known.is_fraud.to_numpy(), winner[3], 1, 10, .10
        )["threshold"]
        held = dedicated_test.loc[dedicated_test.scenario == name]
        positives = int(held.is_fraud.sum())
        if positives < 200:
            raise ValueError(f"{name} has only {positives} positives; requires >=200")
        scores = winner[2].predict_proba(held[FEATURES])[:, 1]
        outcome = threshold_metrics(held.is_fraud.to_numpy(), scores, threshold)
        positive_hits = (scores[held.is_fraud.to_numpy() == 1] >= threshold).astype(float)
        result[name] = {
            "model": winner[1], "dedicated_test_seed": seed + 900003,
            "dedicated_test_rows": test_rows, "type_events": len(held),
            "type_positives": positives, "known_type_validation_rows": len(validation_known),
            "threshold_chosen_on_known_validation": threshold,
            "confusion_matrix": outcome["confusion_matrix"],
            "recall": outcome["recall"],
            "recall_ci95_positive_row_bootstrap": bootstrap_interval(positive_hits.tolist())["ci95_percentile"],
            "limitations": "Within-type positive-row bootstrap ignores episode/customer dependence; synthetic only.",
        }
    return result


def run(seeds: int = 10, count: int = 12000, heldout_rows: int = 30000) -> dict:
    if seeds < 3:
        raise ValueError("At least three seeds required for smoke evaluation")
    runs = []
    for seed in range(42, 42 + seeds):
        with TemporaryDirectory(prefix="sentinel-v6-") as directory:
            metrics = train(count=count, seed=seed, output_dir=Path(directory))
            forced_off = train(count=count, seed=seed, output_dir=Path(directory) / "forced-off",
                               force_no_calibration=True)
        positives = round(metrics["test_fraud_rate"] * metrics["test_rows"])
        row = {
            "seed": seed, "test_seed": metrics["test_seed"], "test_rows": metrics["test_rows"],
            "test_positives": positives, "calibration_method": metrics["calibration_method"],
            "platt_enabled": metrics["calibration_method"] == "disjoint Platt sigmoid",
            "pr_auc": metrics["pr_auc"], "roc_auc": metrics["roc_auc"],
            "forced_off_pr_auc": forced_off["pr_auc"],
            "budgets": {},
        }
        for budget in ALERT_BUDGETS:
            key = str(budget)
            scores = {name: metrics["comparison"][name]["exact_test_top_k"][key]
                      for name in MODELS}
            row["budgets"][key] = {
                "alerts": scores["ml_calibrated"]["alerts"],
                "recall_arithmetic_ceiling": min(1.0, scores["ml_calibrated"]["alerts"] / positives),
                "fraud_typology_expected_precision_ceiling": max(
                    SCENARIOS[name]["positive_rate"] for name in FRAUD_TYPES),
                "models": scores,
                "ml_minus_rule": {metric: scores["ml_calibrated"][metric] - scores["fixed_rules"][metric]
                                  for metric in METRICS},
            }
        row["forced_off_exact_5pct"] = forced_off["comparison"]["ml_calibrated"]["exact_test_top_k"]["0.05"]
        runs.append(row)
    summaries = {"pr_auc": summarize(runs, "pr_auc"),
                 "forced_off_pr_auc": summarize(runs, "forced_off_pr_auc"),
                 "budgets": {}}
    for budget in ALERT_BUDGETS:
        key = str(budget)
        summaries["budgets"][key] = {
            "models": {
                model: {metric: bootstrap_interval([
                    row["budgets"][key]["models"][model][metric] for row in runs
                ]) for metric in METRICS}
                for model in MODELS
            },
            "ml_minus_rule": {metric: bootstrap_interval([
                row["budgets"][key]["ml_minus_rule"][metric] for row in runs
            ]) for metric in METRICS},
            "recall_arithmetic_ceiling": bootstrap_interval([
                row["budgets"][key]["recall_arithmetic_ceiling"] for row in runs
            ]),
        }
    summaries["forced_off_exact_5pct"] = {metric: bootstrap_interval([
        row["forced_off_exact_5pct"][metric] for row in runs
    ]) for metric in METRICS}
    return {
        "method": "Independent synthetic seed-level percentile bootstrap; descriptive, not bank uncertainty",
        "seeds": seeds, "rows_per_development_seed": count,
        "new_test_seed_range": [runs[0]["test_seed"], runs[-1]["test_seed"]],
        "rule_provenance": "Frozen hand rule authored with knowledge of this generator; not independent. Human review recommended.",
        "precision_ceiling_note": "Typology p=0.88 is an approximate expected ceiling, not a deterministic finite-sample bound; other labels/noise and selection can change observed precision.",
        "runs": runs, "summary": summaries,
        "held_out_typologies": held_out_typologies(test_rows=heldout_rows) if seeds >= 10 else "not run in reduced-seed smoke",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--heldout-rows", type=int, default=30000)
    parser.add_argument("--output", type=Path, default=Path("data/v6_evaluation.json"))
    args = parser.parse_args()
    result = run(args.seeds, args.rows, args.heldout_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
