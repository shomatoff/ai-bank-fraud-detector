# Reproducible synthetic-only demo

Only synthetic data is used. Python 3.12 is verified; Node.js/Chrome are optional for screenshots. The dashboard is FastAPI-served HTML/JavaScript, not Streamlit. Use a free loopback port; the server must remain running while the browser uses the link.

1. From the project root, create the isolated environment and install dependencies:

   ```bash
   python3 -m venv .venv
   .venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
   .venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
   ```

2. Generate and inspect a reproducible, ignored synthetic CSV:

   ```bash
   .venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
   ```

   This writes `data/synthetic_transactions.csv`. It contains ten artificial features and a stochastic artificial label. Do not place real transactions in this file or form.

3. Train and evaluate:

   ```bash
   .venv/bin/python -m fraud_detector.model
   ```

   The command prints the actual train/validation/independent-test metrics and writes ignored local artifacts in `data/`. Compare the output with [`MODEL_EVALUATION.md`](MODEL_EVALUATION.md). Re-running with the same software versions and seed should reproduce the metrics.

4. Launch the local app in a terminal:

   ```bash
   .venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
   ```

   Open `http://127.0.0.1:8000`. Use the language selector for Uzbek, Russian, or English. The **Overview** page shows generated aggregates; **Transactions** supports search/filter; **Model insights** shows held-out metrics, threshold preview, curves, PSI and slices. There are no Streamlit pages.

5. Open **Risk analyzer**. Enter synthetic example values: amount `2400`, hour `14`, category `groceries`, channel `card_present`, country risk `0`, new device `Yes`, transactions in one hour `6`, distance `12`, account age `800`, prior declines `2`. Select **Calculate risk**. Inspect the score, model-based linear reasons, and separate descriptive rules. Neither is causal.

6. On first v6-local launch, the app creates two random keys in ignored, owner-only `data/local-api-keys.json`. Read the `analyst` key **only on your own computer** and enter it in the password-style API-key field on **Risk analyzer** *before opening Reports*. Enter `Synthetic review only` and select **Save local report**. In **Reports**, load its ID; an analyst can move `new → in_review → false_positive`. Setting `confirmed_fraud` requires the separate `admin` key in the same input. Inspect the local audit and export JSON, HTML, PDF or report-list CSV. **All** report reads/exports require the API key; writes additionally require CSRF. The key is held in browser session storage for this local demo; clear the session when done. Never use private notes or expose the service. This is annotation only; no bank action occurs.

7. Optional API smoke checks in another terminal:

   ```bash
   curl -fsS http://127.0.0.1:8000/api/health
   curl -fsS http://127.0.0.1:8000/api/metrics
   curl -fsS 'http://127.0.0.1:8000/api/transactions?limit=5'
   ```

   `GET /api/reports/{id}` returns a saved report's detail, and `GET /api/reports/{id}/export` downloads its JSON. The browser handles the per-process CSRF token; local report writes also need the analyst/admin key. For a full live synthetic API check, run `.venv/bin/python -m scripts.live_smoke --base http://127.0.0.1:8000`.

8. Verify the project and recapture real browser screenshots while the server is running:

   ```bash
   .venv/bin/python -m pytest -q
   .venv/bin/ruff check fraud_detector tests scripts
   .venv/bin/pip-audit
   APP_PORT=8000 node scripts/capture.mjs
   ```

Stop the server with `Ctrl+C` when finished. No external service, banking API, payment, or card-block action is involved.
