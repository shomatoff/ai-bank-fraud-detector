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

For write operations, read the per-process token from `GET /api/config`, then send it as `X-CSRF-Token` to `POST /api/reports` or `PATCH /api/reports/{id}`. `PATCH` accepts status `new`, `in_review`, `confirmed_fraud` or `false_positive` and a note up to 300 characters; allowed transitions and note-only changes are recorded in local audit history. `GET /api/reports/{id}/audit` reads it. JSON, HTML, PDF and report-list CSV exports are available through the dashboard/API. Do not put identifiers or private facts in notes.

The optional Dockerfile runs only this local lab: `docker build -t sentinelai-local .` then `docker run --rm -p 127.0.0.1:8000:8000 sentinelai-local`. The container's generated artifacts are ephemeral unless an explicitly managed synthetic-only volume is mounted. Docker execution was not verified in the local audit; Python virtual environment installation was verified.
