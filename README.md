# SentinelAI — AI Bank Fraud Detector

**Current status (2026-10-18):** The GitHub repository is **private**; cloning requires access. The active local model remains v6. An interaction-based challenger improved ordinary synthetic ranking but failed a separate unseen-fraud-type promotion gate and was **not deployed**. See the [full Uzbek experiment and failure report](docs/AI_CHALLENGER_EVALUATION_UZ.md) and [training roadmap](docs/AI_TRAINING_ROADMAP_UZ.md). Neither model has been validated on real bank data.

**v6 synthetic audit (no new release):** The primary result is the mean of **10 new synthetic test seeds (400045–400054)**. At exact 5% alert volume, logistic ML precision is **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**, and PR-AUC **.7455 [.7219,.7656]** (95% seed-bootstrap intervals). Paired ML-minus-rule differences are precision **+.2387 [.2233,.2520]** and recall **+.1923 [.1786,.2045]**. The previously unseen `card_testing` type remains badly detected: recall **.0127 [.0025,.0254]** in a dedicated synthetic test. These numbers do **not** establish real-bank performance. [Current evaluation](docs/MODEL_EVALUATION.md) · [benchmark status](docs/BENCHMARK.md) · [Uzbek documentary](docs/PROJECT_DOCUMENTARY_UZ.md) · [English documentary](docs/PROJECT_DOCUMENTARY_EN.md). Historical v2/v5 measurements are [archived](docs/archive/MODEL_EVALUATION_V2_V5.md); the changed generator and test seeds make the before/after comparison non-causal.

**Synthetic-only local fraud monitoring lab.** FastAPI serves an HTML/CSS/JavaScript dashboard in English, O‘zbek and Русский. No bank data, live payment API, automatic blocking or production-readiness claim. [O‘zbek qo‘llanma](docs/README_UZ.md) · [Русское руководство](docs/README_RU.md).

## Linux download and launch

Python 3.12 is the verified version. Download the source ZIP from [GitHub](https://github.com/shomatoff/ai-bank-fraud-detector) or clone it, then run the following in the project directory:

```bash
git clone https://github.com/shomatoff/ai-bank-fraud-detector.git
cd ai-bank-fraud-detector
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m scripts.v6_evaluation --seeds 10 --rows 12000
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/** while the terminal stays running. Port 8001 works with `--port 8001`, but the link will work only while that server is actually running on your own computer. `/api/health` and `/docs` are on the same port. Use `Ctrl+C` to stop. `make install`, `make data`, `make train`, `make test`, `make lint`, `make run`, `make audit` are convenience targets. For runtime-only installation, use `requirements.txt` with the same constraints file. The constraints record verified main versions; other transitive packages can still affect exact reproducibility. Model artifacts/reports are generated locally in gitignored `data/`; never download an untrusted `joblib` artifact.

Dockerfile is included for a **local lab only**. If Docker is installed: `docker build -t sentinelai-local .` then `docker run --rm -p 127.0.0.1:8000:8000 sentinelai-local`. This container command does not persist reports after exit; use an explicitly managed local volume only for synthetic data. Docker is not a real-bank deployment guide. Windows/macOS have not been verified in this release; Linux is the tested target.

## Feature status

`TESTED` means automated or live local verification; `IMPLEMENTED` means code exists but the named environment/workflow was not fully exercised; `PARTIAL` means important limitations remain.

| Capability | Status | Scope / boundary |
|---|---|---|
| Scenario event generator and past-only rolling windows | TESTED | All seven scenarios now span fit/calibration/validation/test; new-account age is event-relative |
| Temporal fit/calibration/validation + fresh seeded test | TESTED | 60/20/20 development; new test seeds 400045–400054 |
| Logistic scoring, conditional Platt, model-based linear reasons | TESTED | Per-seed calibration decision and forced-off comparison; non-causal |
| Always-normal/rule/depth-3 tree/ML baselines | TESTED | Exact 0.5/1/5/10% top-k across 10 seeds; paired ML-rule CI |
| PR/ROC/reliability curves, threshold preview, PSI and slice metrics | TESTED | Synthetic diagnostics only; not production monitoring |
| FastAPI + EN/UZ/RU HTML/JS dashboard | TESTED | Local loopback; **not Streamlit** |
| Strict CSV batch scoring, SQLite analyst status/notes/audit | TESTED | All report reads/exports/writes require local key; writes also require CSRF |
| JSON/HTML/PDF report and report-list CSV export | TESTED | Keyed local responses; no private data should be entered |
| Model/validation artifact SHA256 + local HMAC | TESTED | Key outside `data/`, owner-only; not bank-grade, joblib still unsafe if untrusted |
| Linux venv install, pytest, Ruff and live API/browser checks | TESTED | Exact results in [report](IMPLEMENTATION_REPORT_UZ.md) |
| Dockerfile and Makefile | PARTIAL | Local Docker unavailable; private [CI Docker build/start/health succeeded](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758) |
| v6 GitHub Actions workflow | TESTED | Private [CI run 39065413758](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758): tests/Ruff/audit, reduced 3-seed smoke and Docker job succeeded |
| pip-audit dependency scan | TESTED | Installed local environment: no known advisories after pip upgrade; time-bound finding |
| Public ULB loader, model comparison, SHAP and feedback demo | PARTIAL | Synthetic ULB-schema fixture tested; real ULB CSV not obtained/run |
| Ten-seed synthetic audit and unseen-typology test | TESTED | New seed-level intervals; held-out card testing recall .0127 |
| Real bank integration, customer data, live payments | NOT IMPLEMENTED | Deliberately excluded |
| Automatic card/transaction blocking | NOT IMPLEMENTED | Human review suggestion only |
| Production authentication/RBAC, signed artifacts, tamper-evident audit | NOT IMPLEMENTED | Required before any external deployment |
| Streamlit pages, vulnerability scanning | NOT IMPLEMENTED | FastAPI-served HTML dashboard; fraud monitoring is different |

For v6, read `data/local-api-keys.json` **only on your own machine** and paste the analyst key into the dashboard's password-style input **before reading, creating or exporting reports**; admin key is required to confirm fraud. Never commit or share either key. The HMAC key is separate at `~/.local/share/sentinelai/artifact-signing.key` or `SENTINELAI_HMAC_KEY_FILE`, not inside `data/`. [Local integration instructions](docs/LOCAL_INTEGRATION.md). Public benchmark data are not used by this app.

## Label formula and historical archive

The artificial label is scenario-dependent `1{U < p_s}`. See [English](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md), [O‘zbek](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md), [Русский](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md), and the [scenario table](docs/SYNTHETIC_SCENARIOS.md). It cannot prove individual wrongdoing. Superseded v2–v5 tables are preserved in the [archive](docs/archive/MODEL_EVALUATION_V2_V5.md), not current claims.

## Demo and API

For download, Linux setup and a copyable scoring request, use the [local integration guide](docs/LOCAL_INTEGRATION.md).

Follow the [reproducible walkthrough](docs/DEMO_WALKTHROUGH.md) to generate synthetic data, train, launch, score, investigate and export. API documentation: `http://127.0.0.1:8000/docs`; main routes: `GET /api/health`, `/api/metrics`, `/api/overview`, `/api/transactions`, `/api/review-queue`, `/api/monitoring`, `/api/feedback/summary`, `/api/reports`, `/api/reports/{id}`, `/api/reports/{id}/audit`, exports (`.csv`, `.html`, `.pdf`, JSON); `POST /api/score`, `/api/score/batch`, `/api/threshold/preview`, `/api/reports`; `PATCH /api/reports/{id}`. **All `/api/reports*` read/export/write routes require analyst/admin `X-API-Key`; `/api/feedback/summary` requires admin; writes also require CSRF** from `/api/config`. Host/Origin is restricted to loopback. The CSV batch endpoint accepts exact feature headers, ≤1000 rows and ≤1 MB. Do not submit real data. [Five-stage upgrade and limits](docs/FIVE_STAGE_UPGRADE_UZ.md).

Real browser captures: [screenshots](screenshots/README.md). Detailed audit: [capabilities](docs/FRAUD_DETECTION_CAPABILITIES.md), [evaluation](docs/MODEL_EVALUATION.md), [model card](docs/MODEL_CARD.md), [data card](docs/DATA_CARD.md), [integration roadmap](docs/BANKING_INTEGRATION_ROADMAP.md), [Uzbek implementation report](IMPLEMENTATION_REPORT_UZ.md). [Release notes](release/RELEASE_NOTES.md), [LinkedIn draft](release/LINKEDIN_POST_EN.md) and [Telegram draft](release/TELEGRAM_ZERODAYUZ_UZ.md) are included; social posts have not been published. MIT license; educational/portfolio use.
