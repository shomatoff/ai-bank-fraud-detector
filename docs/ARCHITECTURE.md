# Architecture

## Runtime flow

```text
scripts.generate_data / fraud_detector.event_stream
        -> fraud_detector.training_v2 (fit, calibration, validation, later test)
        -> data/model.joblib + metrics.json + validation.npz
        -> fraud_detector.api_v2.create_app
        -> FastAPI routes + web/index.html, web/app.js, web/styles.css
        -> local browser and synthetic report exports
```

`fraud_detector/api.py` is the stable import surface and re-exports `create_app` from `api_v2.py`. `fraud_detector/features.py` defines the Pydantic transaction contract and the ten model features. `fraud_detector/reporting.py` renders JSON/HTML/PDF/CSV report outputs; SQLite stores local analyst records.

## Boundaries

- The default server command binds to `127.0.0.1`; middleware rejects non-loopback hosts and mismatched origins.
- Generated artifacts and local keys live under `data/` or the user data directory and are not application source inputs.
- `web/` is a static client, not a Streamlit application.
- Model artifacts are loaded only after SHA256 and local HMAC checks. HMAC is an integrity check, not a bank-grade trust root; `joblib` files must remain trusted.

## Prompt deviation

The prompt's preferred layout names `fraud_lab/` and `dashboard/`, and prefers Streamlit. The implemented package names are `fraud_detector/` and `web/`, with FastAPI serving the dashboard. This deviation is now documented here and in the English/Uzbek/Russian guides; it preserves the working API/browser capture architecture and does not claim Streamlit compliance.
