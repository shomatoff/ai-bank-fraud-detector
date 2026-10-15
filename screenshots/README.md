# Application screenshots

These PNG files are captured from the running FastAPI application in headless Google Chrome at 1440×1000, using only generated data. Capture again with:

```bash
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
node scripts/capture.mjs
```

For another local port, start uvicorn with that port and run `APP_PORT=8001 node scripts/capture.mjs`.

The script visits the live pages, submits a synthetic risk analysis, verifies model reasons, threshold diagnostics, PSI/slices, and the analyst status/note audit, saves and exports a local report, switches languages, and saves eight browser screenshots. It asserts the displayed score, report export, and language-specific pages before capture. The browser profile is temporary and removed after capture.
