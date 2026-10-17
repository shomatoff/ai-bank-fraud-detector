"""Reproducible synthetic-only stability and unseen-typology audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from sklearn.metrics import average_precision_score

from fraud_detector.evaluation import select_cost_threshold, threshold_metrics
from fraud_detector.event_stream import generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training import train
from fraud_detector.training_v2 import candidates

FRAUD_TYPES = ("account_takeover", "card_testing", "mule_cashout", "new_account_transfer")


def bootstrap_interval(values: list[float], seed: int = 518, replicates: int = 10000) -> dict:
    data = np.asarray(values, dtype=float)
    if len(data) < 2:
        raise ValueError("At least two independent runs required")
    rng = np.random.default_rng(seed)
    draws = rng.choice(data, size=(replicates, len(data)), replace=True).mean(axis=1)
    return {"mean": float(data.mean()), "ci95_percentile": [float(v) for v in np.quantile(draws, [.025, .975])]}


def held_out_typologies(seed: int = 42, count: int = 12000) -> dict:
    development = generate_event_stream(count, seed)
    test = generate_event_stream(max(500, count // 4), seed + 300003, start="2026-03-01")
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
        test_scores = winner[2].predict_proba(test[FEATURES])[:, 1]
        held = test.scenario == name
        scores = threshold_metrics(test.loc[held, "is_fraud"], test_scores[held], threshold)
        result[name] = {
            "model": winner[1], "validation_rows": len(validation_known),
            "test_rows_of_held_out_type": int(held.sum()),
            "test_positives_of_held_out_type": int(test.loc[held, "is_fraud"].sum()),
            "threshold_from_known_validation": threshold,
            "held_out_type_confusion_matrix": scores["confusion_matrix"],
            "held_out_type_recall": scores["recall"] if test.loc[held, "is_fraud"].sum() >= 30 else None,
            "recall_status": "evaluable" if test.loc[held, "is_fraud"].sum() >= 30 else "not evaluable (<30 positives)",
            "full_test_precision": threshold_metrics(test.is_fraud, test_scores, threshold)["precision"],
            "full_test_alert_rate": threshold_metrics(test.is_fraud, test_scores, threshold)["alert_rate"],
        }
    return result


def run(seeds: int = 10, count: int = 12000) -> dict:
    if seeds < 10:
        raise ValueError("v5 audit requires at least 10 seeds")
    runs = []
    for seed in range(42, 42 + seeds):
        with TemporaryDirectory(prefix="sentinel-v5-seed-") as directory:
            metrics = train(count=count, seed=seed, output_dir=Path(directory))
        at_five = metrics["comparison"]["ml_calibrated"]["exact_test_top_k"]["0.05"]
        runs.append({"seed": seed, "test_seed": metrics["test_seed"],
                     "test_positives": round(metrics["test_fraud_rate"] * metrics["test_rows"]),
                     "exact_5pct_precision": at_five["precision"],
                     "exact_5pct_recall": at_five["recall"],
                     "pr_auc": metrics["pr_auc"],
                     "calibration_method": metrics["calibration_method"]})
    return {
        "method": "10+ independent synthetic seeds; percentile bootstrap over run means, 10000 resamples; descriptive, not bank uncertainty",
        "rows_per_seed": count, "runs": runs,
        "summary": {key: bootstrap_interval([row[key] for row in runs])
                    for key in ("exact_5pct_precision", "exact_5pct_recall", "pr_auc")},
        "held_out_typologies": held_out_typologies(count=count),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--output", type=Path, default=Path("data/v5_evaluation.json"))
    args = parser.parse_args()
    result = run(args.seeds, args.rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
