# Original master-prompt gap analysis

Audit date: 2026-10-18. Source: `AI_BANK_FRAUD_DETECTOR_CODEX_MASTER_PROMPT.md` in the project root. The source prompt was read but not edited. Statuses are evidence-based:

- **IMPLEMENTED** — code/documentation and a repository test or direct file evidence support the requirement.
- **PARTIAL** — a meaningful implementation exists, but a named deliverable, environment, or verification is incomplete.
- **NOT IMPLEMENTED** — the requirement is deliberately absent or no supporting implementation/evidence exists.

The repository is a local v6 working tree. Existing unrelated working-tree changes were preserved. No GitHub push, tag/release, or social publication was performed as part of this audit.

## 0. Reference and environment verification

| Requirement | Status | Evidence / gap |
|---|---|---|
| Inspect the three reference repositories | PARTIAL | `README.md`, `docs/PROJECT_DOCUMENTARY_EN.md`, and release documentation discuss the references and their quality conventions. A fresh network inspection log is not stored in this repository. |
| Work in a separate project without altering unrelated projects | IMPLEMENTED | Project root is `ai-bank-fraud-detector`; the application code is isolated under `fraud_detector/`, `web/`, `scripts/`, `tests/`. |
| Inventory Python/dependencies and local execution | IMPLEMENTED | `requirements*.txt`, `constraints-verified.txt`, `Makefile`, `docs/DEPLOYMENT_LOCAL.md`; Python 3.12 is the documented tested target. |
| Inventory browser/CPU/RAM/ports/package manager | PARTIAL | Loopback port and browser capture commands are documented in `screenshots/README.md`; no durable CPU/RAM inventory is present. |
| Keep an executable plan | IMPLEMENTED | `docs/PLAN.md` records completed and pending audit phases. |

## 1. Product scope and safety boundaries

| Requirement | Status | Evidence / gap |
|---|---|---|
| Offline-friendly synthetic transaction workflow | IMPLEMENTED | `fraud_detector/event_stream.py`, `scripts/generate_data.py`, `README.md`. |
| Real ML risk score and analyst explanation | IMPLEMENTED | `fraud_detector/training_v2.py::CalibratedLogistic`, `api_v2.py::risk_score`, `explain`; `tests/test_upgrade.py`. |
| Filtering, trends and exports | PARTIAL | Overview, transaction list, local reports and JSON/HTML/PDF/CSV exports exist in `api_v2.py`/`web/`; filtering is limited to client search/status rather than the full prompt's time/risk/channel/amount filter set. |
| Educational HTML/PDF report | IMPLEMENTED | `fraud_detector/reporting.py`, `/api/reports/{id}/export.html`, `/export.pdf`, report tests. |
| No real banks, payment rails, customer records or automatic blocking | IMPLEMENTED | API contains no banking connector or block action; boundary is documented in `README.md`, `docs/SECURITY.md`, and `docs/DATASET_AND_LIMITATIONS.md`. |
| Visible synthetic/demo labeling | IMPLEMENTED | UI strings in `web/app.js`/`web/index.html`, API `data_source`, README and report disclaimers. |

## 2. Preferred technology stack and deviations

| Requirement | Status | Evidence / gap |
|---|---|---|
| Python 3.12, pandas/numpy/scikit-learn/joblib/pytest/Ruff | IMPLEMENTED | `requirements.txt`, `requirements-dev.txt`, `constraints-verified.txt`, `fraud_detector/`, CI. |
| FastAPI, Pydantic, Uvicorn REST service | IMPLEMENTED | `fraud_detector/api.py`, `api_v2.py`, CI/tests. |
| Streamlit + Plotly dashboard | NOT IMPLEMENTED | Deliberate deviation: FastAPI serves `web/index.html`, `web/app.js`, and `web/styles.css`. It is documented and justified in `docs/ARCHITECTURE.md`, `docs/README_EN.md`, `docs/README_UZ.md`, and `docs/README_RU.md`. |
| SQLite local history | IMPLEMENTED | `api_v2.py` creates `reports.sqlite3` with report/audit tables. |
| Jinja/HTML plus optional tested PDF | PARTIAL | HTML is generated directly in `fraud_detector/reporting.py`; ReportLab PDF is implemented/tested. Jinja2 is not used. |
| No mandatory cloud/API/Docker dependence | IMPLEMENTED | Local venv/API path is documented; Docker is optional. |
| Localhost binding and API validation | IMPLEMENTED | Uvicorn commands bind to 127.0.0.1; host/origin middleware and Pydantic constraints are tested. |

## 3. Synthetic data design

| Requirement | Status | Evidence / gap |
|---|---|---|
| Reproducible 10,000–30,000 default dataset and configurable smaller CI data | IMPLEMENTED | `generate_event_stream` default 12,000, seed parameter, `scripts/generate_data.py`, tests. |
| Opaque transaction/customer identifiers, timestamp, amount/currency/category/channel/region | PARTIAL | Synthetic customer IDs and event times exist internally; the public model table intentionally omits IDs/event time and has no currency field. Merchant region is represented by `country_risk`, not a named region field. |
| Past-only velocity and failed-attempt features | IMPLEMENTED | Deques in `event_stream.py` are read before current-row insertion; `tests/test_upgrade.py::test_scenarios_and_past_only_rolling_windows`. |
| Ground-truth rules separated from scoring and documented | IMPLEMENTED | `SYNTHETIC_SCENARIOS.md`, three label-formula docs, training pipeline and model-card caveats. |
| Non-trivial imbalance and challenging legitimate examples | IMPLEMENTED | Seven scenarios and noisy rates in `event_stream.py`; benchmark/evaluation docs report limitations. |
| CLI and `--help`, no hidden download | IMPLEMENTED | `scripts/generate_data.py`; no application download path. |
| README warns synthetic learning is not bank validation | IMPLEMENTED | Root README, `docs/DATASET_AND_LIMITATIONS.md`, model docs. |

## 4. ML pipeline and honest evaluation

| Requirement | Status | Evidence / gap |
|---|---|---|
| Transparent persisted baseline pipeline | IMPLEMENTED | Logistic `Pipeline` + `ColumnTransformer` + `OneHotEncoder`/`StandardScaler` in `training_v2.py`; joblib artifact. |
| Chronological fit/calibration/validation and untouched later test | IMPLEMENTED | 60/20/20 development split and later seed in `training_v2.py`; metrics record split sizes/seeds. |
| Threshold selected on validation only | IMPLEMENTED | `choose_threshold`/`select_cost_threshold` consume validation arrays; tests cover policy. |
| Accuracy context plus confusion/precision/recall/F1/PR-AUC/FPR/prevalence | IMPLEMENTED | `evaluation.py`, `metrics.json` schema, `docs/MODEL_EVALUATION.md`, UI model view. |
| Always-legitimate baseline and imbalance rationale | IMPLEMENTED | `compare_baselines`, evaluation docs, README. |
| Versioned metadata and explicit retraining | IMPLEMENTED | `ARTIFACT_VERSION`, seed/split/threshold/features/library metadata in metrics; `fraud_detector.model` is an explicit command. |
| Strict inference and reload consistency | IMPLEMENTED | `Transaction` Pydantic contract, artifact hash/HMAC checks, `tests/test_foundations.py` and `test_upgrade.py`. |
| Faithful linear explanations | IMPLEMENTED | Exact linear contribution calculation in `training_v2.py`, clearly labelled non-causal. |
| Edge cases: empty, one-class, missing category, zero/negative, unseen category, NaN/range/date/threshold | PARTIAL | Pydantic/range/unseen-category and calibration fallback tests exist; malformed dates and every listed edge case do not each have a dedicated regression test. |
| No invented metrics and explicit synthetic caveat | IMPLEMENTED | Current metrics/docs cite generated test seeds and limitations; no production claim. |

## 5. API list

| Prompt endpoint | Status | Implemented route/evidence |
|---|---|---|
| `GET /health` | PARTIAL | Implemented as `GET /api/health`; `/health` itself is absent. Health returns synthetic status without secrets. |
| `GET /api/v1/summary` | PARTIAL | Equivalent `GET /api/overview` and `GET /api/metrics` exist; `/api/v1/summary` is absent and the unversioned deviation is documented in `docs/ARCHITECTURE.md`/README. |
| `GET /api/v1/transactions` with pagination/filters | PARTIAL | `GET /api/transactions?limit=` validates a bounded limit, but has no v1 prefix, offset pagination, or full time/risk/channel/amount filters. |
| `GET /api/v1/transactions/{id}` | NOT IMPLEMENTED | No individual synthetic transaction route exists. |
| `POST /api/v1/score` | PARTIAL | Equivalent validated `POST /api/score` exists with threshold, model explanation and score. |
| `GET /api/v1/model-metrics` | PARTIAL | Equivalent `GET /api/metrics` exists; v1 route absent. |
| `GET /api/v1/alerts` | PARTIAL | Overview exposes flagged counts and UI displays statuses, but there is no dedicated alerts route. |
| `GET /api/v1/report` | PARTIAL | Keyed report list, detail and JSON/HTML/PDF/CSV exports exist under `/api/reports*`; no singular v1 route. |
| Typed schemas, safe errors, bounded inputs, restrictive CORS/local binding/OpenAPI | IMPLEMENTED | Pydantic models, explicit HTTP errors, CSV caps, loopback/origin middleware, FastAPI `/docs`. |
| Fail visibly rather than mock success when model unavailable | IMPLEMENTED | `create_app(..., auto_train=False)` now raises a clear `RuntimeError`; `tests/test_requirements.py`. |

## 6. Dashboard pages and visual design

| Required page | Status | Evidence / gap |
|---|---|---|
| Overview | IMPLEMENTED | `web/index.html` page-overview and `/api/overview` data. |
| Transaction explorer | PARTIAL | Page and search/status filter exist; requested time/risk/channel/amount filters and server pagination are incomplete. |
| Alert investigation | PARTIAL | Risk analyzer and keyed report/status/audit workflow exist; a separate prioritized alerts page is absent. |
| Model performance | IMPLEMENTED | Model page, confusion matrix and held-out metrics in `web/index.html`/`app.js`. |
| Reports | IMPLEMENTED | Local reports and exports are implemented and tested. |
| About/methodology | PARTIAL | Methodology appears in model page and docs; there is no dedicated About page with all requested content. |
| Dark accessible enterprise styling and data-driven states | PARTIAL | `web/styles.css` and live data provide the visual system; loading/error/empty strings exist, but complete accessibility and every requested state are not independently audited. |
| Streamlit/Plotly implementation | NOT IMPLEMENTED | Deliberate FastAPI + static HTML/JS deviation; documented and justified. |

## 7. Three complete languages

| Requirement | Status | Evidence / gap |
|---|---|---|
| UI text/status/controls/errors in Uzbek, Russian and English | IMPLEMENTED | Central `i18n` dictionaries and overlays in `web/app.js`; new `tests/test_requirements.py::test_i18n_has_the_same_effective_keys_in_all_locales`. |
| Language selection persists | IMPLEMENTED | `localStorage` language handling in `web/app.js`. |
| README in three languages | IMPLEMENTED | `README.md`, `docs/README_UZ.md`, `docs/README_RU.md`, and new `docs/README_EN.md`. |

## 8. Screenshots, demo and visual assets

| Required deliverable | Status | Evidence / gap |
|---|---|---|
| Genuine running-app capture workflow | IMPLEMENTED | `scripts/capture.mjs`, `screenshots/README.md`; existing PNGs are documented as browser captures. |
| `docs/screenshots/dashboard-uz.png` | NOT IMPLEMENTED | Existing genuine file is `screenshots/01-overview-uz.png`; exact prompt path/name is absent. No fabricated rename was made. |
| `docs/screenshots/dashboard-ru.png` | NOT IMPLEMENTED | Existing captures use `screenshots/03-model-ru.png`; exact requested path/name absent. |
| `docs/screenshots/dashboard-en.png` | NOT IMPLEMENTED | Existing capture is `screenshots/04-transactions-en.png`; exact requested path/name absent. |
| `docs/screenshots/alerts-demo.png` | NOT IMPLEMENTED | Existing workflow capture names differ; exact requested file absent. |
| `docs/screenshots/transaction-risk-detail.png` | NOT IMPLEMENTED | Existing `screenshots/02-risk-analyzer-uz.png` is a related genuine capture, but the exact required path/name is absent. |
| `docs/screenshots/model-performance.png` | NOT IMPLEMENTED | Existing `screenshots/06-model-diagnostics-ru.png` is a related genuine capture, but exact path/name is absent. |
| Optional 20–30 second demo/storyboard | PARTIAL | Browser workflow exists; no verified video file. Manual storyboard can be derived from `docs/SOCIAL_MEDIA_ASSETS.md`. |
| Truthful social drafts | IMPLEMENTED | New `docs/LINKEDIN_POST_EN.md`, `docs/TELEGRAM_POST_UZ.md`, `docs/SOCIAL_MEDIA_ASSETS.md`; publication not performed. |

## 9. Documentation and file layout

| Requirement | Status | Evidence / gap |
|---|---|---|
| Root README/license/requirements/CI | IMPLEMENTED | Present and linked; CI is `.github/workflows/ci.yml`. |
| Prompt's `fraud_lab/` package | NOT IMPLEMENTED | Actual package is `fraud_detector/`; deliberate package-name deviation documented in `docs/ARCHITECTURE.md`. |
| Prompt's `dashboard/` directory | NOT IMPLEMENTED | Actual frontend is `web/`; documented deviation. |
| Three language guides | IMPLEMENTED | `docs/README_UZ.md`, `docs/README_RU.md`, new `docs/README_EN.md`. |
| `ARCHITECTURE.md` | IMPLEMENTED | New document. |
| `DATASET_AND_LIMITATIONS.md` | IMPLEMENTED | New document. |
| `MODEL_EVALUATION.md` | IMPLEMENTED | Existing evidence document. |
| `SECURITY.md` | IMPLEMENTED | New document. |
| `TESTING.md` | IMPLEMENTED | New document. |
| `DEPLOYMENT_LOCAL.md` | IMPLEMENTED | New document. |
| `CHANGELOG.md` | IMPLEMENTED | New document; distinguishes local v6 from earlier v2.0.0 reference. |
| `PLAN.md` | IMPLEMENTED | New document. |
| `LINKEDIN_POST_EN.md`, `TELEGRAM_POST_UZ.md`, `SOCIAL_MEDIA_ASSETS.md` | IMPLEMENTED | New documents; drafts are explicitly unpublished. |
| README feature table, setup, metrics, limitations and verified links | PARTIAL | Root README is detailed and honest, but it describes the FastAPI deviation and current local state; exact prompt screenshot paths and some v1 API links do not exist. |
| Relative links/image paths checked | PARTIAL | Existing docs and screenshot README provide tested paths; the six prompt-specific `docs/screenshots` paths remain unresolved. |

## 10. Security, privacy and data governance

| Requirement | Status | Evidence / gap |
|---|---|---|
| Synthetic/local/offline default | IMPLEMENTED | Generator, local API, README and new SECURITY/DATASET docs. |
| No unnecessary payload/token logging | IMPLEMENTED | No logging of API keys or full payloads found in production sources; regression scan added. |
| Formula-safe exports and path/input bounds | IMPLEMENTED | `reporting.py`, CSV caps, Pydantic bounds and export tests. |
| No external banking/Telegram/financial automation | IMPLEMENTED | No such call in application; explicitly documented. |
| Governance/fairness/privacy/human oversight disclosure | IMPLEMENTED | `docs/SECURITY.md`, `docs/MODEL_CARD.md`, `docs/BANKING_INTEGRATION_ROADMAP.md`. |
| Production-grade auth/RBAC/key management | NOT IMPLEMENTED | Local analyst/admin keys and HMAC are intentionally not production controls; limitation is documented. |

## 11. Testing, CI and release requirements

| Required test area | Status | Evidence / gap |
|---|---|---|
| Generator determinism/schema | IMPLEMENTED | `tests/test_app.py`. |
| Timestamps/historical-only velocity | IMPLEMENTED | `tests/test_upgrade.py`. |
| Non-leakage/preprocessing | IMPLEMENTED | `tests/test_upgrade.py`, `training_v2.py`. |
| Split and threshold selection | IMPLEMENTED | `tests/test_app.py`, `test_upgrade.py`. |
| Saved model reload consistency | IMPLEMENTED | `tests/test_foundations.py`, `test_upgrade.py`. |
| Risk bounds/input validation | IMPLEMENTED | API tests and Pydantic `Transaction`. |
| Metrics/imbalance | IMPLEMENTED | `evaluation.py`, public benchmark tests and training tests. |
| FastAPI health/scoring/invalid/pagination | IMPLEMENTED | `tests/test_app.py`, `tests/test_foundations.py`. |
| i18n completeness | IMPLEMENTED | New `tests/test_requirements.py`. |
| CSV/JSON accuracy/formula safety | IMPLEMENTED | `tests/test_upgrade.py`, reporting/API tests. |
| Reports | IMPLEMENTED | `tests/test_foundations.py`, `test_upgrade.py`. |
| Empty/unavailable model | IMPLEMENTED | New `tests/test_requirements.py`; explicit `auto_train=False` failure. |
| Privacy/no hard-coded secrets | IMPLEMENTED | New production-source scan plus synthetic-only tests/docs. |
| `pytest -q`, Ruff, smoke and CI | PARTIAL | Local pytest/Ruff are run; CI defines tests/audit/model/Docker jobs; a fresh GitHub run and local Docker run are not part of this audit. |
| v1.0.0 release with attached built artifacts | NOT IMPLEMENTED | Existing documentation references v2.0.0 and current code is v6-local; no new release action was taken. |

## 12. LinkedIn and Telegram assets

| Requirement | Status | Evidence / gap |
|---|---|---|
| English LinkedIn draft with stack/result/caveat/languages/hashtags | IMPLEMENTED | `docs/LINKEDIN_POST_EN.md`. |
| Uzbek Telegram draft for @zerodayuz | IMPLEMENTED | `docs/TELEGRAM_POST_UZ.md`. |
| Capture/design instructions and DEMO label | IMPLEMENTED | `docs/SOCIAL_MEDIA_ASSETS.md`. |
| Publish only after explicit approval | IMPLEMENTED | Drafts state unpublished; no publication tool/action used. |

## 13. Acceptance criteria

| Criterion | Status | Evidence / gap |
|---|---|---|
| One-command or reliable two-process offline startup | PARTIAL | Root README and `docs/DEPLOYMENT_LOCAL.md` provide a reliable sequence; it is several setup/training commands rather than one command. |
| Reproducible data, fitted model, time holdout, calculated metrics | IMPLEMENTED | Generator/training code, metrics artifacts and tests. |
| Real-model scores/thresholds, not random statuses | IMPLEMENTED | Persisted pipeline, threshold metadata, API score and tests. |
| Dashboard main views and validated API | PARTIAL | Main FastAPI views and validated routes work, but prompt's Streamlit pages and v1 route names are not implemented. |
| Three language switches/docs/genuine screenshots | PARTIAL | Language switch/docs and genuine differently named captures exist; six exact prompt screenshot paths are missing. |
| Lint/tests/security/no real data/external banking | PARTIAL | Local tests/lint/security controls pass; Docker/CI fresh run and independent security audit are not verified. |
| README links/downloads resolve to present files | PARTIAL | Existing links are documented; exact prompt screenshot/API paths do not resolve. |
| GitHub/release/social only after approval and exact result | IMPLEMENTED | No publication was attempted in this audit; no new URL/result is claimed. |

## 14. Required final-report format

| Requirement | Status | Evidence / gap |
|---|---|---|
| Uzbek final report divided into COMPLETED / TESTED / BLOCKED / NOT DONE | IMPLEMENTED | This gap analysis and the final handoff use those categories; `docs/PLAN.md` tracks pending verification. |
| Include exact URLs only when created, measured scores with caveats, screenshot/post paths, outstanding limits | IMPLEMENTED | Root README, model/evaluation docs and this matrix use verified paths/URLs only; missing screenshot paths and limitations are explicitly listed. |
| Stop and request approval before GitHub/social publication | IMPLEMENTED | No push/tag/release/social operation was performed here. |

## Verification log for this audit

The focused added tests passed before the full run: `3 passed`. The final full run passed **26 tests** with one existing non-failing LightGBM/SHAP warning; Ruff reported `All checks passed!`. Docker and a fresh hosted GitHub run remain unverified. The master prompt itself remains unchanged (checksum recorded during audit: `7e4f6ebc9c25d39b9a6b5052a3df3c1475d9888a787b025ba64133e017a79cf5`).
