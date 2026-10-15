import json
import sqlite3

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient

from fraud_detector.api import create_app
from fraud_detector.features import FEATURES
from fraud_detector.model import score, train
from fraud_detector.synthetic import generate_transactions
from fraud_detector.training import choose_threshold


def sample_transaction():
    row = generate_transactions(100, 28).iloc[0]
    return {
        key: bool(row[key]) if key == "is_new_device"
        else row[key].item() if hasattr(row[key], "item") else row[key]
        for key in FEATURES
    }


def test_review_budget_threshold_handles_ties():
    scores = np.array([.01] * 90 + [.2] * 10)
    threshold = choose_threshold(scores, .1)
    assert np.mean(scores >= threshold) <= .1
    with pytest.raises(ValueError):
        choose_threshold(scores, 1)


def test_saved_model_matches_api_score(tmp_path):
    metrics = train(count=2000, seed=19, output_dir=tmp_path)
    transaction = sample_transaction()
    model = joblib.load(tmp_path / "model.joblib")
    expected = score(model, transaction)
    client = TestClient(create_app(tmp_path))
    result = client.post("/api/score", json=transaction).json()
    assert result["probability"] == pytest.approx(expected, abs=.00005)
    assert result["threshold"] == metrics["threshold"]
    assert result["review_recommended"] is (expected >= metrics["threshold"])
    assert client.get("/api/metrics").json()["selected_model"] == metrics["selected_model"]


def test_origin_headers_and_input_contract(tmp_path):
    train(count=1000, seed=4, output_dir=tmp_path)
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/health", headers={"Host": "example.com"}).status_code == 403
    assert client.post("/api/score", json={}, headers={"Origin": "http://testserver.evil"}).status_code == 403
    assert client.post("/api/score", json={}, headers={"Origin": "http://localhost:8001"}).status_code == 403
    assert client.get("/").headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in client.get("/").headers["content-security-policy"]
    assert client.get("/api/health").headers["cache-control"] == "no-store"
    assert client.post("/api/score", json={**sample_transaction(), "customer_name": "Private"}).status_code == 422


def test_report_migration_details_and_json_export(tmp_path):
    train(count=1000, seed=5, output_dir=tmp_path)
    old_db = tmp_path / "reports.sqlite3"
    with sqlite3.connect(old_db) as db:
        db.execute("""CREATE TABLE reports (id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL, probability REAL NOT NULL, level TEXT NOT NULL,
            transaction_json TEXT NOT NULL, note TEXT NOT NULL)""")
    client = TestClient(create_app(tmp_path))
    with sqlite3.connect(old_db) as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(reports)")}
    assert {"model_name", "threshold"} <= columns
    assert old_db.stat().st_mode & 0o077 == 0
    transaction = sample_transaction()
    payload = {"transaction": transaction, "note": "Synthetic investigation"}
    assert client.post("/api/reports", json=payload).status_code == 403
    token = client.get("/api/config").json()["csrf_token"]
    created = client.post("/api/reports", json=payload, headers={"X-CSRF-Token": token})
    assert created.status_code == 201
    report_id = created.json()["id"]
    detail = client.get(f"/api/reports/{report_id}").json()
    assert detail["transaction"] == transaction
    assert detail["model_name"] in {"logistic_regression", "logistic_regularized"}
    assert detail["data_source"] == "synthetic"
    assert "card_number" not in json.dumps(detail)
    exported = client.get(f"/api/reports/{report_id}/export")
    assert exported.status_code == 200
    assert exported.json() == detail
    assert "attachment;" in exported.headers["content-disposition"]
    assert client.get("/api/reports/999999/export").status_code == 404
