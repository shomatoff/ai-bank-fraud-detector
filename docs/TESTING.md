# Testing and verification

The test suite is run with the repository environment:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check fraud_detector tests scripts
.venv/bin/pip-audit
```

The tests cover deterministic generation and schema, historical-only rolling features, chronological split and threshold selection, preprocessing/model reload consistency, bounded Pydantic/API inputs, metrics and imbalance baselines, API health/scoring/pagination, report authentication/CSRF/status/audit/export behavior, i18n key parity, formula-safe exports, no production hard-coded secret material, and empty/unavailable model behavior. `scripts/live_smoke.py` and `scripts/capture.mjs` exercise a real loopback server/browser; their commands are documented in `screenshots/README.md` and `docs/DEMO_WALKTHROUGH.md`.

The GitHub workflow runs Ruff, pytest, pip-audit, model training and a reduced multi-seed smoke. It also defines a Docker build/health job. Docker was not available in the local verification environment, so local Docker success is not claimed. Windows/macOS tests are not claimed.
