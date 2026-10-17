"""Predeclared synthetic challenger audit; never changes the deployed artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.metrics import average_precision_score

from fraud_detector.evaluation import exact_top_k_metrics
from fraud_detector.event_stream import generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training_v2 import candidates, interaction_candidate


def evaluate(seeds: range, count: int) -> dict:
    runs = []
    for seed in seeds:
        development = generate_event_stream(count, seed, start="2026-01-01")
        test = generate_event_stream(max(3000, count // 4), seed + 500003,
                                     start="2026-03-01")
        fit = development.iloc[:int(.6 * count)]
        validation = development.iloc[int(.8 * count):]
        base_candidates = candidates(seed)
        for model in base_candidates.values():
            model.fit(fit[FEATURES], fit.is_fraud)
        base_name = max(base_candidates, key=lambda name: average_precision_score(
            validation.is_fraud,
            base_candidates[name].predict_proba(validation[FEATURES])[:, 1],
        ))
        challenger = interaction_candidate(seed).fit(fit[FEATURES], fit.is_fraud)
        row = {"seed": seed, "test_seed": seed + 500003,
               "fit_rows": len(fit), "validation_rows": len(validation),
               "test_rows": len(test), "baseline_selected_on_validation": base_name,
               "models": {}}
        for name, model in (("baseline", base_candidates[base_name]),
                            ("interaction_challenger", challenger)):
            validation_scores = model.predict_proba(validation[FEATURES])[:, 1]
            test_scores = model.predict_proba(test[FEATURES])[:, 1]
            row["models"][name] = {
                "validation_pr_auc": float(average_precision_score(validation.is_fraud, validation_scores)),
                "validation_exact_5pct": exact_top_k_metrics(
                    validation.is_fraud, validation_scores, .05),
                "test_pr_auc": float(average_precision_score(test.is_fraud, test_scores)),
                "test_exact_5pct": exact_top_k_metrics(test.is_fraud, test_scores, .05),
            }
        row["selected_on_validation"] = max(
            row["models"], key=lambda name: (
                row["models"][name]["validation_exact_5pct"]["precision"],
                row["models"][name]["validation_pr_auc"],
            ),
        )
        runs.append(row)
    def mean(model: str, field: str) -> float:
        def selected(row: dict) -> dict:
            name = row["selected_on_validation"] if model == "validation_selected" else model
            return row["models"][name]
        if field == "test_pr_auc":
            return sum(selected(row)[field] for row in runs) / len(runs)
        return sum(selected(row)["test_exact_5pct"][field] for row in runs) / len(runs)
    return {
        "protocol": "Seeds, features and comparison fixed before fresh March test scoring; synthetic only.",
        "runs": runs,
        "mean": {name: {metric: mean(name, metric) for metric in
                        ("test_pr_auc", "precision", "recall")}
                 for name in ("baseline", "interaction_challenger", "validation_selected")},
        "production_artifact_changed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-seed", type=int, default=142)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--output", type=Path, default=Path("data/challenger_evaluation.json"))
    args = parser.parse_args()
    if args.seeds < 3 or args.rows < 1000:
        parser.error("Use at least three seeds and 1000 development rows")
    result = evaluate(range(args.first_seed, args.first_seed + args.seeds), args.rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result["mean"], indent=2))


if __name__ == "__main__":
    main()
