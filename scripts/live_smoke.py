"""Exercise a running loopback API with only synthetic transactions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--keys", type=Path, default=Path("data/local-api-keys.json"))
    args = parser.parse_args()
    keys = json.loads(args.keys.read_text())
    item = {"amount": 2400, "hour": 14, "merchant_category": "groceries",
            "channel": "card_present", "country_risk": 0, "is_new_device": True,
            "velocity_1h": 6, "distance_km": 12, "account_age_days": 800,
            "prior_declines_24h": 2}
    outcomes = {}
    with httpx.Client(base_url=args.base, timeout=15) as client:
        for path in ("/", "/docs", "/api/health", "/api/metrics", "/api/overview",
                     "/api/transactions?limit=5"):
            outcomes[f"GET {path}"] = client.get(path).status_code
        outcomes["GET /api/reports without key"] = client.get("/api/reports").status_code
        outcomes["GET /api/reports analyst"] = client.get(
            "/api/reports", headers={"X-API-Key": keys["analyst"]}).status_code
        outcomes["POST /api/score"] = client.post("/api/score", json=item).status_code
        outcomes["POST /api/score/batch malformed"] = client.post(
            "/api/score/batch", content="bad\n1\n", headers={"Content-Type": "text/csv"}
        ).status_code
        csrf = client.get("/api/config").json()["csrf_token"]
        payload = {"transaction": item, "note": "Synthetic v5 smoke"}
        outcomes["POST report without key"] = client.post(
            "/api/reports", json=payload, headers={"X-CSRF-Token": csrf}
        ).status_code
        analyst_headers = {"X-CSRF-Token": csrf, "X-API-Key": keys["analyst"]}
        created = client.post("/api/reports", json=payload, headers=analyst_headers)
        outcomes["POST report analyst"] = created.status_code
        if created.status_code == 201:
            report_id = created.json()["id"]
            outcomes["PATCH in_review analyst"] = client.patch(
                f"/api/reports/{report_id}", json={"status": "in_review", "note": "Smoke review"},
                headers=analyst_headers,
            ).status_code
            outcomes["PATCH confirmed analyst"] = client.patch(
                f"/api/reports/{report_id}", json={"status": "confirmed_fraud"},
                headers=analyst_headers,
            ).status_code
            outcomes["PATCH confirmed admin"] = client.patch(
                f"/api/reports/{report_id}", json={"status": "confirmed_fraud"},
                headers={"X-CSRF-Token": csrf, "X-API-Key": keys["admin"]},
            ).status_code
            for suffix in ("/audit", "/export", "/export.html", "/export.pdf"):
                outcomes[f"GET report{suffix} without key"] = client.get(
                    f"/api/reports/{report_id}{suffix}").status_code
                outcomes[f"GET report{suffix}"] = client.get(
                    f"/api/reports/{report_id}{suffix}", headers=analyst_headers).status_code
            outcomes["GET reports/export.csv without key"] = client.get(
                "/api/reports/export.csv").status_code
            outcomes["GET reports/export.csv"] = client.get(
                "/api/reports/export.csv", headers=analyst_headers).status_code
    print(json.dumps(outcomes, indent=2))
    expected = {"POST /api/score/batch malformed": 422, "POST report without key": 401,
                "GET /api/reports without key": 401,
                "POST report analyst": 201, "PATCH in_review analyst": 200,
                "PATCH confirmed analyst": 403, "PATCH confirmed admin": 200}
    expected.update({key: 401 for key in outcomes if key.endswith("without key")})
    if any(outcomes.get(key) != value for key, value in expected.items()) or any(
        value != 200 for key, value in outcomes.items() if key not in expected
    ):
        raise SystemExit("Live smoke failed")


if __name__ == "__main__":
    main()
