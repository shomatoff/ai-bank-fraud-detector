# AI Bank Fraud Detector — English guide

This is a local, synthetic-only fraud-risk analysis laboratory. FastAPI serves an HTML/CSS/JavaScript dashboard in English, Uzbek and Russian; it does not connect to a bank, process payments, or block accounts. The root [README](../README.md) contains the verified Linux quick start, current synthetic evaluation summary and links to the detailed evidence.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. The application generates only synthetic records. Tests and limitations are documented in [TESTING](TESTING.md), [DATASET_AND_LIMITATIONS](DATASET_AND_LIMITATIONS.md), and [SECURITY](SECURITY.md).

## Deliberate implementation choices

The master prompt prefers Streamlit, but this repository uses FastAPI plus a static HTML/JavaScript client. The choice is documented in [ARCHITECTURE](ARCHITECTURE.md) because the existing API, browser capture workflow and local security middleware are built around FastAPI. The current artifact/model version is v6; this is a local project version, not a claim that the requested v1.0.0 release exists.

## Scope

The model is trained on generated transactions with chronological development splits and a later synthetic test seed. Scores and explanations are model outputs or explicitly labelled descriptive signals; they are not proof of fraud, calibrated real-world probabilities, or production performance.
