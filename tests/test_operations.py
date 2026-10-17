from datetime import UTC, datetime, timedelta

import numpy as np
import pytest
from fastapi.testclient import TestClient

from fraud_detector.api_v2 import create_app
from fraud_detector.evaluation import select_cost_threshold, threshold_metrics
from fraud_detector.features import FEATURES
from fraud_detector.label_policy import feedback_summary
from fraud_detector.operations import (
    RateLimiter,
    possible_card_testing_burst,
    review_queue,
)
from fraud_detector.synthetic import generate_transactions


def test_card_testing_hint_is_fallible_and_does_not_change_rank():
    legitimate_lookalike = {
        "amount": 8, "channel": "online", "is_new_device": True,
        "velocity_1h": 3, "prior_declines_24h": 0,
    }
    assert possible_card_testing_burst(legitimate_lookalike)
    rows = [legitimate_lookalike, {**legitimate_lookalike, "amount": 100}]
    assert review_queue(rows, [0.1, 0.9], 1) == [{
        "id": "SYN-00002", "probability": 0.9,
        "possible_card_testing_burst": False,
    }]
    with pytest.raises(ValueError):
        review_queue(rows, [0.1, float("nan")], 2)


def test_delayed_labels_exclude_pending_and_recent_terminal():
    now = datetime(2026, 10, 18, tzinfo=UTC)
    def row(status, days):
        return {"status": status,
                "created_at": (now - timedelta(days=30)).isoformat(),
                "updated_at": (now - timedelta(days=days)).isoformat()}
    result = feedback_summary([
        row("new", 20), row("in_review", 20), row("confirmed_fraud", 8),
        row("false_positive", 1),
    ], as_of=now)
    assert result["unknown"] == 1
    assert result["pending"] == 1
    assert result["confirmed_fraud"] == 1
    assert result["analyst_false_positive"] == 1
    assert result["matured_eligible"] == 1
    assert result["training_automatic"] is False
    with pytest.raises(ValueError):
        feedback_summary([row("unverified", 8)], as_of=now)
    with pytest.raises(ValueError):
        feedback_summary([{**row("confirmed_fraud", 8), "updated_at": now.isoformat(),
                           "created_at": (now + timedelta(days=1)).isoformat()}], as_of=now)
    with pytest.raises(ValueError):
        feedback_summary([row("confirmed_fraud", -1)], as_of=now)


def test_rate_limiter_window_and_independent_clients():
    now = [0.0]
    limiter = RateLimiter(clock=lambda: now[0])
    assert limiter.check("a", limit=2) == 0
    assert limiter.check("a", limit=2) == 0
    assert limiter.check("a", limit=2) == 60
    assert limiter.check("b", limit=2) == 0
    now[0] = 60.0
    assert limiter.check("a", limit=2) == 0


def test_fast_threshold_matches_exhaustive_policy():
    rng = np.random.default_rng(211)
    for size in (4, 20, 200):
        labels = rng.integers(0, 2, size=size)
        scores = rng.integers(0, 7, size=size) / 10
        for budget in (.1, .5, 1.0):
            candidates = np.r_[np.nextafter(scores.max(), np.inf), np.unique(scores)]
            eligible = []
            for threshold in candidates:
                result = threshold_metrics(labels, scores, threshold)
                if result["alert_rate"] <= budget + 1e-12:
                    matrix = result["confusion_matrix"]
                    cost = matrix["fp"] + 10 * matrix["fn"]
                    eligible.append(((cost, -result["recall"], threshold), result))
            expected_key, expected = min(eligible, key=lambda item: item[0])
            actual = select_cost_threshold(labels, scores, 1, 10, budget)
            assert actual == {**expected, "estimated_cost": float(expected_key[0])}
    with pytest.raises(ValueError):
        select_cost_threshold([0, 1], [0.1, float("nan")], 1, 10)


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    return TestClient(create_app(tmp_path_factory.mktemp("operations")))


def test_queue_monitoring_and_api_security(client):
    queue = client.get("/api/review-queue?capacity=3")
    assert queue.status_code == 200
    items = queue.json()["items"]
    assert len(items) == 3
    assert [item["probability"] for item in items] == sorted(
        [item["probability"] for item in items], reverse=True
    )
    assert all(set(item) == {"id", "probability", "possible_card_testing_burst"} for item in items)
    assert client.get("/api/review-queue?capacity=101").status_code == 422
    monitoring = client.get("/api/monitoring").json()
    assert monitoring["live_telemetry_available"] is False
    assert monitoring["rollback_automatic"] is False
    assert client.get("/api/feedback/summary").status_code == 401
    keys = client.app.state.local_api_keys
    assert client.get("/api/feedback/summary", headers={"X-API-Key": keys["analyst"]}).status_code == 403
    assert client.get("/api/feedback/summary", headers={"X-API-Key": keys["admin"]}).json()["pending"] == 0

    row = generate_transactions(100, 217).iloc[0]
    transaction = {key: (bool(row[key]) if key == "is_new_device" else
                         row[key].item() if hasattr(row[key], "item") else row[key])
                   for key in FEATURES}
    assert client.post("/api/score", json={**transaction, "cvv": "123"}).status_code == 422
    assert client.post("/api/score", json={**transaction, "pin": "1234"}).status_code == 422
    assert client.post("/api/score", json={**transaction, "pan": "4111111111111111"}).status_code == 422
    client.app.state.rate_limiter = RateLimiter()
    client.app.state.rate_limits["score"] = 1
    try:
        assert client.post("/api/score", json=transaction).status_code == 200
        limited = client.post("/api/score", json=transaction)
        assert limited.status_code == 429
        assert int(limited.headers["Retry-After"]) >= 1
    finally:
        client.app.state.rate_limits["score"] = 120
