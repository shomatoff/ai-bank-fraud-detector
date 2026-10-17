"""Guard the opt-in challenger against target and future-event leakage."""

import numpy as np
import pandas as pd
import pytest

from fraud_detector.event_stream import generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training_v2 import (
    augment_interaction_features,
    candidates,
    interaction_candidate,
)
from scripts.heldout_promotion_gate import promotion_decision


def test_interactions_use_only_model_inputs():
    stream = generate_event_stream(1200, 303)
    features = stream[FEATURES]
    original = augment_interaction_features(features)
    changed_metadata = stream.copy()
    changed_metadata["is_fraud"] = 1 - changed_metadata.is_fraud
    changed_metadata["scenario"] = "unknown"
    changed_metadata["event_time"] = pd.Timestamp("2030-01-01", tz="UTC")
    assert original.equals(augment_interaction_features(changed_metadata[FEATURES]))
    assert np.isfinite(original.select_dtypes(include="number").to_numpy()).all()
    assert all(column in original for column in (
        "small_online_new_device", "small_amount_velocity",
        "new_device_velocity", "young_account_transfer",
    ))


def test_challenger_scores_and_keeps_original_schema():
    stream = generate_event_stream(1200, 304)
    model = interaction_candidate(304).fit(stream.iloc[:900][FEATURES], stream.iloc[:900].is_fraud)
    probabilities = model.predict_proba(stream.iloc[900:][FEATURES])[:, 1]
    assert probabilities.shape == (300,)
    assert np.isfinite(probabilities).all()
    assert ((probabilities >= 0) & (probabilities <= 1)).all()


def test_rejected_challenger_is_not_deployed_without_new_gate():
    assert "interaction_challenger" not in candidates(42)
    decision = promotion_decision({
        "account_takeover": {"baseline_recall": .74, "challenger_recall": .0},
        "card_testing": {"baseline_recall": .01, "challenger_recall": .01},
    })
    assert decision["promote"] is False
    assert decision["regression_failures"] == ["account_takeover"]
    assert decision["minimum_recall_failures"] == ["account_takeover", "card_testing"]
    assert decision["failed_typologies"] == ["account_takeover", "card_testing"]


def test_gate_rejects_empty_or_nonfinite_metrics():
    with pytest.raises(ValueError, match="requires typologies"):
        promotion_decision({})
    with pytest.raises(ValueError, match="challenger_recall must be finite"):
        promotion_decision({"card_testing": {
            "baseline_recall": .1, "challenger_recall": float("nan"),
        }})
