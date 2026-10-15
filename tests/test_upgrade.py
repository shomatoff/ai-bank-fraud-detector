import csv
import io
import json
from collections import defaultdict, deque

import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient

from fraud_detector.api import create_app
from fraud_detector.evaluation import population_stability_index, select_cost_threshold
from fraud_detector.event_stream import SCENARIOS, generate_event_stream
from fraud_detector.features import FEATURES
from fraud_detector.training import explain, score, train


@pytest.fixture(scope="module")
def upgraded(tmp_path_factory):
    directory = tmp_path_factory.mktemp("v4-upgrade")
    metrics = train(count=1600, seed=31, output_dir=directory)
    return directory, metrics, TestClient(create_app(directory))


def transaction():
    row = generate_event_stream(100, 91).iloc[0]
    return {
        key: bool(row[key]) if key == "is_new_device"
        else row[key].item() if hasattr(row[key], "item") else row[key]
        for key in FEATURES
    }


def test_scenarios_and_past_only_rolling_windows():
    stream = generate_event_stream(1200, 17)
    assert stream.equals(generate_event_stream(1200, 17))
    assert set(SCENARIOS) <= set(stream.scenario)
    assert stream.event_time.is_monotonic_increasing
    seen: dict[str, deque] = defaultdict(deque)
    bad: dict[str, deque] = defaultdict(deque)
    for row in stream.itertuples(index=False):
        history = seen[row.customer_id]
        declines = bad[row.customer_id]
        while history and history[0] <= row.event_time.timestamp() - 3600:
            history.popleft()
        while declines and declines[0] <= row.event_time.timestamp() - 86400:
            declines.popleft()
        assert row.velocity_1h == len(history)
        assert row.prior_declines_24h == len(declines)
        history.append(row.event_time.timestamp())
        if row.is_declined:
            declines.append(row.event_time.timestamp())
    assert stream.loc[stream.scenario == "legit_travel", "is_fraud"].mean() < .5
    assert stream.loc[stream.scenario == "card_testing", "is_fraud"].mean() > .5


def test_temporal_split_comparators_and_monitoring(upgraded):
    _, metrics, _ = upgraded
    assert metrics["artifact_version"] == 4
    assert metrics["train_rows"] == 1040
    assert metrics["calibration_rows"] == 160
    assert metrics["validation_rows"] == 400
    assert metrics["test_rows"] == 500
    assert metrics["test_seed"] == 200034
    times = metrics["time_split"]
    assert times["fit_end"] <= times["calibration_start"]
    assert times["calibration_end"] <= times["validation_start"]
    assert times["validation_end"] < times["test_start"]
    assert metrics["selected_model"] == max(metrics["validation_pr_auc"], key=metrics["validation_pr_auc"].get)
    assert set(metrics["comparison"]) == {"always_normal", "fixed_rules", "ml_calibrated"}
    for candidate in metrics["comparison"].values():
        assert set(candidate["budgets"]) == {"0.05", "0.1"}
        for result in candidate["budgets"].values():
            assert sum(result["confusion_matrix"].values()) == 500
    assert metrics["comparison"]["always_normal"]["budgets"]["0.1"]["alerts"] == 0
    assert set(metrics["monitoring"]["slices"]) == {"channel", "country_risk", "account_age"}
    assert population_stability_index(np.arange(1000), np.arange(1000) * 1.5) > 0


def test_calibrated_linear_explanation_is_exact(upgraded):
    directory, metrics, client = upgraded
    model = joblib.load(directory / "model.joblib")
    item = transaction()
    detail = explain(model, item)
    assert detail["method"] == "exact_linear_contributions_to_calibrated_log_odds"
    reconstructed = detail["intercept"] + sum(x["contribution"] for x in detail["all_contributions"])
    assert reconstructed == pytest.approx(detail["calibrated_log_odds"], abs=1e-10)
    probability = 1 / (1 + np.exp(-reconstructed))
    assert score(model, item) == pytest.approx(probability, abs=1e-10)
    response = client.post("/api/score", json=item)
    assert response.status_code == 200
    assert response.json()["model_explanation"]["top_reasons"]
    assert response.json()["signals_type"] == "hand_written_descriptive_rules"
    assert response.json()["threshold"] == metrics["threshold"]


def test_validation_cost_policy_and_preview(upgraded):
    _, metrics, client = upgraded
    response = client.post("/api/threshold/preview", json={
        "false_positive_cost": 2, "false_negative_cost": 11, "review_budget": .05,
    })
    assert response.status_code == 200
    value = response.json()
    assert value["source"] == "validation synthetic labels only"
    assert value["alert_rate"] <= .05
    assert value["not_a_test_or_live_performance_estimate"] is True
    slider = client.post("/api/threshold/preview", json={"threshold": .5})
    assert slider.status_code == 200
    assert slider.json()["validation_rows"] == metrics["validation_rows"]
    with pytest.raises(ValueError):
        select_cost_threshold(np.array([0, 1]), np.array([.1, .9]), -1, 1)


def test_artifact_hash_rejects_tampering(tmp_path):
    train(count=1000, seed=81, output_dir=tmp_path)
    path = tmp_path / "model.joblib"
    with path.open("ab") as file:
        file.write(b"tamper")
    with pytest.raises(RuntimeError, match="hash mismatch"):
        create_app(tmp_path)


def test_review_audit_exports_and_batch(upgraded):
    _, _, client = upgraded
    item = transaction()
    token = client.get("/api/config").json()["csrf_token"]
    created = client.post("/api/reports", json={"transaction": item, "note": "Synthetic case"},
                          headers={"X-CSRF-Token": token})
    assert created.status_code == 201
    report_id = created.json()["id"]
    assert client.patch(f"/api/reports/{report_id}", json={"status": "in_review"}).status_code == 403
    assert client.post("/api/reports", json={
        "transaction": item, "card_number": "must-reject"
    }, headers={"X-CSRF-Token": token}).status_code == 422
    first = client.patch(f"/api/reports/{report_id}", json={"status": "in_review", "note": "Review started"},
                         headers={"X-CSRF-Token": token})
    assert first.status_code == 200
    note_only = client.patch(f"/api/reports/{report_id}", json={
        "status": "in_review", "note": "Updated investigation note"
    }, headers={"X-CSRF-Token": token})
    assert note_only.status_code == 200
    assert note_only.json()["note"] == "Updated investigation note"
    assert client.patch(f"/api/reports/{report_id}", json={
        "status": "in_review", "note": "Updated investigation note"
    }, headers={"X-CSRF-Token": token}).status_code == 409
    assert client.patch(f"/api/reports/{report_id}", json={"status": "new"},
                        headers={"X-CSRF-Token": token}).status_code == 409
    final = client.patch(f"/api/reports/{report_id}", json={
        "status": "false_positive", "note": "Synthetic false alert"
    }, headers={"X-CSRF-Token": token})
    assert final.status_code == 200
    assert final.json()["status"] == "false_positive"
    audit = client.get(f"/api/reports/{report_id}/audit").json()
    assert [entry["action"] for entry in audit] == ["created", "status_change", "note_change", "status_change"]
    assert client.get("/api/reports/export.csv").status_code == 200
    assert client.get(f"/api/reports/{report_id}/export").json()["status"] == "false_positive"
    html = client.get(f"/api/reports/{report_id}/export.html")
    assert html.status_code == 200 and "Synthetic false alert" in html.text
    pdf = client.get(f"/api/reports/{report_id}/export.pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FEATURES)
    writer.writeheader()
    writer.writerow(item)
    batch = client.post("/api/score/batch", content=output.getvalue(),
                        headers={"Content-Type": "text/csv"})
    assert batch.status_code == 200
    assert len(list(csv.DictReader(io.StringIO(batch.text)))) == 1
    invalid = client.post("/api/score/batch", content="card_number\n123\n",
                          headers={"Content-Type": "text/csv"})
    assert invalid.status_code == 422
    bad_boolean = client.post("/api/score/batch", content=output.getvalue().replace(
        ",True,", ",yes,").replace(",False,", ",yes,"),
        headers={"Content-Type": "text/csv"})
    assert bad_boolean.status_code == 422
    oversized = client.post("/api/score/batch", content=b"x" * 1_000_001,
                            headers={"Content-Type": "text/csv"})
    assert oversized.status_code == 413
    assert json.loads((upgraded[0] / "metrics.json").read_text())["production_ready"] is False


def test_report_exports_escape_analyst_text(upgraded):
    _, _, client = upgraded
    token = client.get("/api/config").json()["csrf_token"]
    created = client.post("/api/reports", json={
        "transaction": transaction(), "note": "  =<script>alert(1)</script>"
    }, headers={"X-CSRF-Token": token})
    assert created.status_code == 201
    report_id = created.json()["id"]
    html = client.get(f"/api/reports/{report_id}/export.html").text
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    rows = list(csv.DictReader(io.StringIO(client.get("/api/reports/export.csv").text)))
    exported = next(row for row in rows if row["id"] == str(report_id))
    assert exported["note"].startswith("'  =")
