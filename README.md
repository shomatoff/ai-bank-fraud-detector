# SentinelAI — AI Bank Fraud Detector

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
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/** while the terminal stays running. Port 8001 works with `--port 8001`, but the link will work only while that server is actually running on your own computer. `/api/health` and `/docs` are on the same port. Use `Ctrl+C` to stop. `make install`, `make data`, `make train`, `make test`, `make lint`, `make run`, `make audit` are convenience targets. For runtime-only installation, use `requirements.txt` with the same constraints file. The constraints record verified main versions; other transitive packages can still affect exact reproducibility. Model artifacts/reports are generated locally in gitignored `data/`; never download an untrusted `joblib` artifact.

Dockerfile is included for a **local lab only**. If Docker is installed: `docker build -t sentinelai-local .` then `docker run --rm -p 127.0.0.1:8000:8000 sentinelai-local`. This container command does not persist reports after exit; use an explicitly managed local volume only for synthetic data. Docker is not a real-bank deployment guide. Windows/macOS have not been verified in this release; Linux is the tested target.

## Feature status

`TESTED` means automated or live local verification; `IMPLEMENTED` means code exists but the named environment/workflow was not fully exercised; `PARTIAL` means important limitations remain.

| Capability | Status | Scope / boundary |
|---|---|---|
| Scenario event generator and past-only rolling windows | TESTED | Four fraud-like, two legitimate edge scenarios; noisy artificial labels |
| Temporal fit/calibration/validation + fresh seeded test | TESTED | Test never used to select default model or threshold |
| Logistic scoring, Platt sigmoid, model-based linear reasons | TESTED | Linear non-causal explanation; calibration worsened test Brier |
| Always-normal/rule/ML baselines at alert budgets | TESTED | Deployable validation cutoffs plus retrospective same-volume view |
| PR/ROC/reliability curves, threshold preview, PSI and slice metrics | TESTED | Synthetic diagnostics only; not production monitoring |
| FastAPI + EN/UZ/RU HTML/JS dashboard | TESTED | Local loopback; **not Streamlit** |
| Strict CSV batch scoring, SQLite analyst status/notes/audit | TESTED | Synthetic inputs; local audit is not tamper-evident |
| JSON/HTML/PDF report and report-list CSV export | TESTED | Local files/responses; no private data should be entered |
| Model/validation artifact SHA256 integrity checks | TESTED | Integrity only, not authenticity/signature |
| Linux venv install, pytest, Ruff and live API/browser checks | TESTED | Exact results in [report](IMPLEMENTATION_REPORT_UZ.md) |
| Dockerfile and Makefile | IMPLEMENTED | Docker runtime not verified unless report says otherwise |
| GitHub Actions workflow | TESTED | Public GitHub `main` push run passed; final run link in [report](IMPLEMENTATION_REPORT_UZ.md) |
| pip-audit dependency scan | TESTED | Installed local environment: no known advisories after pip upgrade; time-bound finding |
| Real bank integration, customer data, live payments | NOT IMPLEMENTED | Deliberately excluded |
| Automatic card/transaction blocking | NOT IMPLEMENTED | Human review suggestion only |
| Production authentication/RBAC, signed artifacts, tamper-evident audit | NOT IMPLEMENTED | Required before any external deployment |
| Streamlit pages, vulnerability scanning | NOT IMPLEMENTED | FastAPI-served HTML dashboard; fraud monitoring is different |

## Executed model result

The new scenario/event-stream generator creates 12,000 development rows (65% fit, 10% calibration, 25% validation) and a **new, later, seeded 3,000-row synthetic test**. At the validation-selected threshold .08581994158148241, test prevalence is 176/3000 (5.8667%), precision .707627, recall .948864, F1 .810680, PR-AUC .893556 and ROC AUC .977438; TN2755 FP69 FN9 TP167. These are simulator results, not bank effectiveness. The v3 result under a different generator was precision .1009, recall .3548, PR-AUC .1134; this before/after comparison is **not** a controlled algorithm-only gain. Calibration increased Brier error from .012016 to .012800; card-present recall was 0/4. Full baselines and caveats: [MODEL_EVALUATION](docs/MODEL_EVALUATION.md).

The v4 artificial label formula is scenario-dependent `1{U < p_s}`, **not** the retired v3 sigmoid equation. Learn the parameters and examples in [English](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md), [O‘zbek](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md), [Русский](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md), and the [scenario table](docs/SYNTHETIC_SCENARIOS.md). These labels cannot prove individual wrongdoing.

## Demo and API

For download, Linux setup and a copyable scoring request, use the [local integration guide](docs/LOCAL_INTEGRATION.md).

Follow the [reproducible walkthrough](docs/DEMO_WALKTHROUGH.md) to generate synthetic data, train, launch, score, investigate and export. API documentation: `http://127.0.0.1:8000/docs`; main routes: `GET /api/health`, `/api/metrics`, `/api/overview`, `/api/transactions`, `/api/reports`, `/api/reports/{id}`, `/api/reports/{id}/audit`, exports (`.csv`, `.html`, `.pdf`, JSON); `POST /api/score`, `/api/score/batch`, `/api/threshold/preview`, `/api/reports`; `PATCH /api/reports/{id}`. Writes require local CSRF token from `/api/config` and local Host/Origin. The CSV batch endpoint accepts exact feature headers, ≤1000 rows and ≤1 MB. Do not submit real data.

Real browser captures: [screenshots](screenshots/README.md). Detailed audit: [capabilities](docs/FRAUD_DETECTION_CAPABILITIES.md), [evaluation](docs/MODEL_EVALUATION.md), [model card](docs/MODEL_CARD.md), [data card](docs/DATA_CARD.md), [integration roadmap](docs/BANKING_INTEGRATION_ROADMAP.md), [Uzbek implementation report](IMPLEMENTATION_REPORT_UZ.md). [Release notes](release/RELEASE_NOTES.md), [LinkedIn draft](release/LINKEDIN_POST_EN.md) and [Telegram draft](release/TELEGRAM_ZERODAYUZ_UZ.md) are included; social posts have not been published. MIT license; educational/portfolio use.
