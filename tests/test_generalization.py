import numpy as np
import pytest

from fraud_detector.event_stream import generate_event_stream
from fraud_detector.generalization import (
    customer_temporal_split,
    customer_top_k_metrics,
)
from scripts.audit_generalization import evaluate


def test_customer_cohort_split_is_temporal_and_disjoint():
    stream = generate_event_stream(5000, 842)
    parts = customer_temporal_split(stream, seed=842)
    assert set(parts["fit"].customer_id).isdisjoint(parts["new_customer_test"].customer_id)
    assert set(parts["validation"].customer_id).isdisjoint(parts["new_customer_test"].customer_id)
    assert set(parts["seen_test"].customer_id) <= (
        set(parts["fit"].customer_id) | set(parts["validation"].customer_id)
    )
    assert parts["fit"].event_time.max() < parts["validation"].event_time.min()
    assert parts["validation"].event_time.max() < parts["new_customer_test"].event_time.min()
    assert set(parts["seen_test"].customer_id).isdisjoint(parts["new_customer_test"].customer_id)
    assert sum(len(part) for part in parts.values()) < len(stream)  # early heldout events are excluded


def test_customer_top_k_counts_one_case_per_customer():
    outcome = customer_top_k_metrics([1, 1, 0, 0], [.9, .8, .7, .6],
                                     ["A", "A", "B", "C"], budget=.34)
    assert outcome["customers"] == 3
    assert outcome["review_capacity"] == 2
    assert outcome["positive_customers"] == 1
    assert outcome["hit_customers"] == 1
    assert outcome["precision"] == .5
    with pytest.raises(ValueError):
        customer_top_k_metrics([1], [np.nan], ["A"])


def test_nonchronological_stream_rejected():
    stream = generate_event_stream(1000, 18).iloc[::-1]
    with pytest.raises(ValueError):
        customer_temporal_split(stream)


def test_audit_smoke_never_promotes_active_model():
    result = evaluate(seed=842, rows=5000)
    assert result["active_model_changed"] is False
    assert result["selected_model"] in result["validation_pr_auc"]
    assert result["cohorts"]["new_customer_test"]["rows"] > 0
