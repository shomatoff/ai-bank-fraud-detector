"""Synthetic-only, customer-disjoint temporal audit helpers."""
from __future__ import annotations

import hashlib
import math

import numpy as np
import pandas as pd


def customer_temporal_split(frame: pd.DataFrame, seed: int = 842,
                            holdout_fraction: float = .20) -> dict[str, pd.DataFrame]:
    """Reserve whole synthetic customers, then use chronological windows.

    Holdout customers are absent from fitting and validation, but their earlier
    synthetic events can still inform past-only event-history features.
    """
    if (not .05 <= holdout_fraction <= .5 or len(frame) < 100
            or not frame.event_time.is_monotonic_increasing
            or frame.customer_id.isna().any()):
        raise ValueError("Expected >=100 chronological rows and valid customer IDs")
    ids = sorted(frame.customer_id.unique())
    if len(ids) < 10:
        raise ValueError("At least 10 distinct customers are required")
    ranked = sorted(ids, key=lambda value: hashlib.sha256(f"{seed}:{value}".encode()).digest())
    held_ids = set(ranked[:round(len(ids) * holdout_fraction)])
    fit_end, validation_end = int(.6 * len(frame)), int(.8 * len(frame))
    fit = frame.iloc[:fit_end].loc[lambda rows: ~rows.customer_id.isin(held_ids)]
    validation = frame.iloc[fit_end:validation_end].loc[
        lambda rows: ~rows.customer_id.isin(held_ids)
    ]
    later = frame.iloc[validation_end:]
    seen_ids = set(fit.customer_id) | set(validation.customer_id)
    seen_test = later.loc[later.customer_id.isin(seen_ids)]
    new_customer_test = later.loc[later.customer_id.isin(held_ids)]
    if any(part.empty or part.is_fraud.nunique() < 2
           for part in (fit, validation, seen_test, new_customer_test)):
        raise ValueError("Each split requires positive and negative synthetic labels")
    return {"fit": fit, "validation": validation, "seen_test": seen_test,
            "new_customer_test": new_customer_test}


def customer_top_k_metrics(labels, scores, customer_ids, budget: float = .05) -> dict:
    """Count distinct synthetic customers, not repeated transactions."""
    labels = np.asarray(labels)
    scores = np.asarray(scores, dtype=float)
    ids = np.asarray(customer_ids)
    if (not 0 < budget <= 1 or len(scores) == 0 or len(labels) != len(scores)
            or len(ids) != len(scores) or not np.isfinite(scores).all()
            or not np.isin(labels, [0, 1]).all() or pd.isna(ids).any()):
        raise ValueError("Use matched finite scores, binary labels and customer IDs")
    grouped = pd.DataFrame({"customer_id": ids, "score": scores,
                            "label": labels}).groupby("customer_id", sort=True).agg(
        score=("score", "max"), label=("label", "max")
    )
    count = len(grouped)
    capacity = max(1, math.ceil(count * budget))
    ranked = grouped.sort_values("score", ascending=False, kind="stable")
    positives = int(grouped.label.sum())
    hits = int(ranked.head(capacity).label.sum())
    return {"customers": count, "positive_customers": positives,
            "review_capacity": capacity, "hit_customers": hits,
            "precision": hits / capacity,
            "recall": hits / positives if positives else None,
            "meaning": "Synthetic customer-level top-k; no real card or account IDs"}
