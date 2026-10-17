import json

import pytest
from fastapi.testclient import TestClient

from fraud_detector.api import create_app
from fraud_detector.features import FEATURES
from fraud_detector.model import train
from fraud_detector.synthetic import generate_transactions


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    directory = tmp_path_factory.mktemp("artifacts")
    train(count=1600, seed=7, output_dir=directory)
    return TestClient(create_app(directory))


@pytest.fixture
def transaction():
    row = generate_transactions(100, seed=99).iloc[0]
    return {key: (bool(row[key]) if key == "is_new_device" else row[key].item() if hasattr(row[key], "item") else row[key]) for key in FEATURES}


def test_generator_is_reproducible_and_has_no_identifiers():
    a = generate_transactions(1000, 17)
    b = generate_transactions(1000, 17)
    assert a.equals(b)
    assert set(a.columns) == set(FEATURES) | {"is_fraud"}
    assert 0 < a.is_fraud.sum() < len(a)


def test_training_metrics_are_held_out(tmp_path):
    m = train(count=2000, seed=9, output_dir=tmp_path)
    assert m["train_rows"] == 1200 and m["calibration_rows"] == 400 and m["validation_rows"] == 400 and m["test_rows"] == 500
    assert sum(m["confusion_matrix"].values()) == 500
    assert m["artifact_version"] == 6
    assert m["test_seed"] == 400012
    assert m["selected_model"] == max(m["validation_pr_auc"], key=m["validation_pr_auc"].get)
    assert 0 < m["review_budget"] < 1
    assert 0 <= m["pr_auc"] <= 1
    assert 0 <= m["roc_auc"] <= 1
    assert json.loads((tmp_path / "metrics.json").read_text()) == m


def test_dashboard_and_api(client, transaction):
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json()["data_source"] == "synthetic"
    assert client.get("/api/overview").json()["transactions"] == 1000
    assert len(client.get("/api/transactions?limit=5").json()) == 5
    assert client.get("/api/transactions?limit=101").status_code == 422
    result = client.post("/api/score", json=transaction)
    assert result.status_code == 200
    assert 0 <= result.json()["probability"] <= 1
    assert client.post("/api/score", json={**transaction, "amount": -1}).status_code == 422
    assert client.post("/api/score", json={**transaction, "card_number": "secret"}).status_code == 422


def test_reports_require_csrf_and_store_only_allowed_fields(client, transaction):
    payload = {"transaction": transaction, "note": "Synthetic review"}
    assert client.post("/api/reports", json=payload).status_code == 403
    token = client.get("/api/config").json()["csrf_token"]
    assert client.post("/api/reports", json=payload, headers={"X-CSRF-Token": token}).status_code == 401
    response = client.post("/api/reports", json=payload, headers={
        "X-CSRF-Token": token, "X-API-Key": client.app.state.local_api_keys["analyst"]})
    assert response.status_code == 201
    assert client.get("/api/reports").status_code == 401
    assert client.get("/api/reports", headers={"X-API-Key": client.app.state.local_api_keys["analyst"]}).json()[0]["note"] == "Synthetic review"


def test_local_host_and_origin_restrictions(client):
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 403
    assert client.post("/api/score", json={}, headers={"Origin": "https://evil.example"}).status_code == 403
