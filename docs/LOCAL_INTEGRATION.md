# Local synthetic API integration

This guide demonstrates integration with a **local synthetic lab**. It does not authorize real customer data, live payments, card actions or bank network access. The server binds to `127.0.0.1`; all commands below run on the same machine. See [capabilities](FRAUD_DETECTION_CAPABILITIES.md), [evaluation](MODEL_EVALUATION.md) and the [banking boundary](BANKING_INTEGRATION_ROADMAP.md).

## Install and start on verified Linux/Python 3.12

```bash
git clone https://github.com/shomatoff/ai-bank-fraud-detector.git
cd ai-bank-fraud-detector
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements.txt
.venv/bin/python -m fraud_detector.model
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the dashboard or `http://127.0.0.1:8000/docs` for OpenAPI. The local server must be running. Use `curl -fsS http://127.0.0.1:8000/api/health` for a readiness check; expected `data_source` is `synthetic`. Default model artifacts and reports are created in ignored `data/` and are not shipped in the source ZIP.

## Score one synthetic event

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/score \
  -H 'Content-Type: application/json' \
  -d '{"amount":2400,"hour":14,"merchant_category":"groceries","channel":"card_present","country_risk":0,"is_new_device":true,"velocity_1h":6,"distance_km":12,"account_age_days":800,"prior_declines_24h":2}'
```

The response has a synthetic score, a validation selected threshold, `review_recommended`, separate descriptive `signals`, and linear `model_explanation.top_reasons`. Keep the `signals` separate from learned contributions. The recommendation has no effect on payments.

## Batch CSV and analyst reports

`POST /api/score/batch` accepts `Content-Type: text/csv`, an exact ten column header in the order shown below, UTF-8, at most 1,000 rows and 1,000,000 bytes. `is_new_device` must be `true` or `false` (case insensitive). Invalid, extra or missing columns are rejected.

```text
amount,hour,merchant_category,channel,country_risk,is_new_device,velocity_1h,distance_km,account_age_days,prior_declines_24h
2400,14,groceries,card_present,0,true,6,12,800,2
```

Upload a local synthetic CSV with `curl -fsS -X POST http://127.0.0.1:8000/api/score/batch -H 'Content-Type: text/csv' --data-binary @synthetic-input.csv -o scored.csv`. The dashboard also provides this upload/download flow.

For v6-local **all `/api/reports*` reads, exports and writes require** an analyst/admin `X-API-Key`; writes also require the per-process CSRF token from `GET /api/config`. On first launch, two random API keys are written with owner-only permissions to ignored `data/local-api-keys.json`. Read your `analyst` key locally and paste it into the dashboard’s password-style input before opening Reports; never paste it into public documentation, screenshots, logs or chat. You may instead set **both** `SENTINELAI_ANALYST_KEY` and `SENTINELAI_ADMIN_KEY` (distinct, at least 20 characters). `confirmed_fraud` requires admin. These are limited local demo controls, **not** production identity, rotation, RBAC or secure storage. `PATCH` accepts `new`, `in_review`, `confirmed_fraud` or `false_positive` and a note up to 300 characters; transitions and note changes enter SQLite audit history. JSON, HTML, PDF and CSV exports require the key header, including direct API clients. Never enter private data or expose the loopback service to a network. The artifact HMAC key is **separate** from API keys and lives outside `data/` at `~/.local/share/sentinelai/artifact-signing.key` unless `SENTINELAI_HMAC_KEY_FILE` points to another owner-only path. It is still not a bank-grade external trust root; `joblib` remains unsafe for untrusted artifacts.

The optional Dockerfile runs only this local lab: `docker build -t sentinelai-local .` then `docker run --rm -p 127.0.0.1:8000:8000 sentinelai-local`. Its generated artifacts and keys are ephemeral unless managed synthetic-only volumes are mounted. The v6 local `docker build -t sentinelai-v6-local .` attempt returned `docker: command not found` (exit 127); build/run/container health are **not verified**. A CI Docker job was added but has **not yet run**. Python virtual environment and loopback API were verified.

## 2026-10-18 local review additions

`GET /api/review-queue?capacity=20` returns exactly 1–100 top-scoring synthetic items, sorted by the unchanged active ML score. The `possible_card_testing_burst` flag is descriptive only and does not affect ranking or decisions. `GET /api/monitoring` shows fixed synthetic-sample alert volume and prior validation/test diagnostics, **not live telemetry**. `GET /api/feedback/summary` requires the **admin** `X-API-Key` and separates unknown, pending, terminal analyst statuses and 7-day-matured terminal statuses; it never triggers training. Score, batch, report writes and expensive analytics now have in-process per-client rate limits and may return `429` plus `Retry-After`. These are local controls, not production API security; see [five-stage upgrade and limits](FIVE_STAGE_UPGRADE_UZ.md).

2026-10-18 follow-up: the **local machine still has no verified Docker run**, but the private [GitHub Actions CI job](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758) successfully built the image, started a container and passed `/api/health`. This does not verify production/container security or persistence.
