# SentinelAI: from zero to one hundred — an evidence-based documentary

This is a **technical chronology** with film-style chapter titles, not invented dialogue or events. Sources: Git commits `4da0fb3`, `07b05da`, `0babd0d`; the pre-v5 part of the [v2 report](../IMPLEMENTATION_REPORT_UZ.md); [v4 evaluation](MODEL_EVALUATION.md); current `fraud_detector/`, `tests/`, `scripts/` and executed v5 outputs. The earliest prototypes have no commits in this repository; their exact dates and step-by-step logs are **not recorded**. “One hundred” closes this story; it does not mean product maturity or bank readiness.

## Chapter 1. The idea: observe a safe laboratory, not a bank

The boundary is explicit: no real bank records, customers, credentials, live payment APIs or automatic blocking. `README.md`, `docs/BANKING_INTEGRATION_ROADMAP.md` and `fraud_detector/api_v2.py` describe only local synthetic monitoring. The interface is not Streamlit: FastAPI serves `web/index.html`, CSS and JavaScript. The v2 report records that the master prompt was not found in the workspace/Desktop search; its contents and completion percentage cannot be verified.

## Chapter 2. The workspace: Python, tests and boundaries

The code is divided among `fraud_detector/`, `web/`, `scripts/`, `tests/` and `docs/`, with an isolated `.venv`. Python 3.12, FastAPI, scikit-learn, NumPy/pandas, SQLite, HTML/CSS/JS, pytest, Ruff, pip-audit and Chrome CDP are evidenced by the v2 report, requirement files and `scripts/capture.mjs`. The exact date the first local folder was created is **not recorded**. `Dockerfile` and `Makefile` exist, but the v5 `docker build -t sentinelai-v5-local .` returned `/bin/bash: docker: command not found` (exit 127); the image was not shown to work.

## Chapter 3. First generator, first model: a lesson against trusting a number

The older v3 label mechanism was `Bernoulli(sigmoid(z))`, preserved as history in the [label formula](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md). The v2 report records v3 test precision `.1009`, recall `.3548`, PR-AUC `.1134`, ROC AUC `.7714`. Its exact commit and full logs are **not recorded** in current Git history. Poor precision meant many false alerts. The lesson was to expose the simulation assumptions, not decorate the test result. The generator changed between v3 and v4, so their numbers are not a controlled algorithm-only gain.

## Chapter 4. v3 to v4: scenarios and an event stream

`fraud_detector/event_stream.py` creates four fraud-like types (`account_takeover`, `card_testing`, `mule_cashout`, `new_account_transfer`), legitimate travel and large purchases, and normal events. It computes `velocity_1h` and `prior_declines_24h` from deques **before** inserting the current row into history. `tests/test_upgrade.py::test_scenarios_and_past_only_rolling_windows` independently recomputes them row by row. Scenario, ID and label are excluded from model inputs. This limits row-level future leakage but does not remove simulator coupling between features and labels; external validity is absent.

## Chapter 5. Time-aware evaluation and baselines

In `fraud_detector/training_v2.py`, v4 split development into 7,800 fit, 1,200 calibration and 3,000 validation rows, followed by 3,000 independent later test rows; model C and threshold were chosen on validation. `fraud_detector/evaluation.py` computes always-normal, rule and logistic baselines. V4 test: TP167 FP69 FN9 TN2755, precision `.707627`, recall `.948864`, PR-AUC `.893556` ([exact table](MODEL_EVALUATION.md)). Yet the historical table shows that a nominal 5% ML cutoff flagged 232/3000 = **7.733%** of the test. That was not a same-volume comparison. V5 makes exact top-k at 0.5/1/5/10% primary and keeps validation cutoffs separately with actual alert percentages.

## Chapter 6. The analyst's hand, the system's limit

`fraud_detector/api_v2.py` scores one transaction, validates a CSV batch, and stores `new → in_review → confirmed_fraud/false_positive`, notes and audit entries in SQLite. `fraud_detector/reporting.py` supplies JSON/HTML/PDF/CSV exports. `coefficient × standardized value` explains the model calculation; hand-written API signals are separate. Neither proves causality. No code blocks a card or payment. `tests/test_upgrade.py` exercises status, note-only audit, exports and invalid input.

## Chapter 7. First error ledger — problems recorded before v5

Each row states observation → location/evidence → cause, fix and outcome. When the original commit is unavailable, it is **not recorded**.

| Observation | Where and evidence | Cause, fix, result |
|---|---|---|
| A tiny calibration slice crashed | `training_v2.py`; v2 report says calibration contained one class | `LogisticRegression` needs two classes. `IdentityCalibrator` fallback was added; tests passed. Initial stack trace **not recorded**. |
| Ruff objected to an unnecessary int cast | v2 report, Ruff check | Cast removed; later Ruff said `All checks passed`. Original source line **not recorded**. |
| CSV body was read fully | `api_v2.py::batch_score`, v2 report | Streaming 1 MB and 1,000-row caps added; oversized test returns 413. |
| Note-only edits were impossible | `api_v2.py::update_review`, v2 report | Added `note_change` audit for same status/different note; API and Chrome checks passed. |
| PDF could cut long UZ/RU words | `reporting.py`, v2 report `pdftotext` check | Glyph-width wrapping and page continuation; 18/18 Uzbek and 18/18 Russian examples were read back. |
| CSV formula risk and lax validation | `api_v2.py`, `reporting.py`, v2 report/tests | Restrict CSV boolean to `true/false`, reject extra JSON fields, quote formulas after leading spaces; regression tests passed. |
| Older pip had advisories | v2 report: 12 advisories for pip 24.0 | Isolated `.venv` upgraded to pip 26.2.1; then `pip-audit` reported “No known vulnerabilities found” at that time. Not certification. |
| Patch `.orig/.rej` remnants | v2 report lists 11 files | Only work-generated temporary copies were removed; no user data removed. |

## Chapter 8. CI and the public v2.0.0 release

Git history: `4da0fb3` initial release commit, `07b05da` CI/report update, `0babd0d` verified-CI link. [GitHub Actions run 38786481512](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/38786481512) succeeded; [v2.0.0 release](https://github.com/shomatoff/ai-bank-fraud-detector/releases/tag/v2.0.0) was published. Old Node warnings from `actions/checkout`/`setup-python` led to `@v7` and Ubuntu 24.04; final v2 CI passed. This **does not** mean v5 is on GitHub: v5 stays local without new push/release approval.

## Chapter 9. The v5 audit: a harder task, lower numbers

`event_stream.py` gained `legit_many_declines`; fraud scenario positive probability fell `.94→.88`, normal noise rose `.005→.01`. Fit/calibration/validation became 60/20/20. The first v5 calculation was noticed to reuse old test seed 200045. `training_v2.py` and `scripts/v5_evaluation.py` were changed to the **new** 300045 and 300045–300054 family, and results were recomputed. The intermediate reused-seed result was precision `.640816`, recall `.844086`, PR-AUC `.713471` — **not final v5**. The final new test yielded TP164 FP90 FN25 TN2721, precision `.645669`, recall `.867725`, PR-AUC `.796689`. It is below v2 too, but generator, split and test seed changed together; one cause cannot be isolated.

Across 10 full-pipeline seeds, exact-5% mean precision was `.813333` (95% seed-bootstrap [.800667,.828667]), recall `.661446` ([.648752,.674807]), PR-AUC `.731488` ([.715733,.750300]); see `scripts/v5_evaluation.py` and generated, uncommitted `data/v5_evaluation.json`. Leaving one type out of training and validation gave **card testing TP0/FN41** in its test slice. At the default threshold, card-present was TP0/FN14, but 14 positives are too few for a stable subgroup recall; the UI says `not evaluable (<30 positives)`.

## Chapter 10. Second error ledger — v5

| Observation | Where and evidence | Cause, fix, result |
|---|---|---|
| Old CSRF-only test expected 201, got 401 | `tests/test_foundations.py::test_report_migration_details_and_json_export`, pytest: 1 failed / 15 passed | New `X-API-Key` was required. Test updated with key; final result in [v5 report](../IMPLEMENTATION_REPORT_UZ.md#qoshimcha-hisobot-v5). |
| Ruff imports and `BLE001` | `fraud_detector/api_v2.py`, `public_benchmark.py`, `tests/test_public_benchmark.py`; Ruff output | Imports sorted, broad `Exception` narrowed to known optional-explainer failures; Ruff passed again. |
| Larger Platt worsened validation | `training_v2.py`: Brier `.017899→.018520`, ECE `.014630→.018282` | “Calibration always helps” was false. Identity used unless both improve; final model is raw logistic. |
| Hash alone could be rewritten | Old SHA256-only `api_v2.py`; `tests/test_upgrade.py::test_artifact_hmac_rejects_rewritten_hashes` | Added HMAC over artifact hashes with a local 0600 key, verified before `joblib.load`. Key is co-located: not bank-grade. |
| ULB source URL returned HTTP 404 | `curl -I -L` on `https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud` | Unauthenticated endpoint was unavailable here; no credential or workaround was used. Loader tested on synthetic fixture; **no real ULB result**. |
| XGBoost install requested a 305 MB CUDA dependency | `.venv/bin/python -m pip install xgboost shap` output | Unnecessary download stopped; `lightgbm==4.7.0`, `shap==0.53.0` installed. **No XGBoost result**. |
| LightGBM SHAP warning | pytest: 18 passed, 1 warning; `shap/explainers/_tree.py:579` | Upstream list/array output difference; `public_benchmark.py::_explanation` normalizes both. Warning remains visible. |
| Feedback demo got worse | 300-row **synthetic fixture**, `data/fixture_benchmark_results.json` | Idealized 30 validation labels for retraining: test PR-AUC `.152906→.124331`, exact-5% TP `1→0`; not real analyst feedback. |
| Docker build could not run | `docker build -t sentinelai-v5-local .`: exit 127 | `docker` absent; container build/run/health **not recorded**. Local venv API health returned 200. |

## Chapter 11. What we got wrong

Final local recheck (2026-10-16): `pytest -q` — **21 passed, 1 LightGBM/SHAP warning**; `ruff check fraud_detector tests scripts` — **All checks passed**; `pip-audit` — **No known vulnerabilities found**; `pip check` — **No broken requirements found**. `scripts/live_smoke.py` returned the expected 200/201/401/403/422 statuses in 19 HTTP checks; Chrome captured 9 genuine screenshots. All 24 Markdown files had zero broken local links. These results do not substitute for Docker or a real public-dataset benchmark.

“Nominal 5%” was not actual 5%: v2 ML flagged 7.733%, v5 8.4%. Synthetic labels and distinctive scenarios can inflate apparent quality. Platt worsened v4 test Brier `.012016→.012800` and did not help v5 validation. Card-present was TP0/FN4 in v4 and TP0/FN14 in v5; tiny slices do not support reliable recall estimates. High aggregate recall does **not** imply discovery of new fraud: held-out card testing was TP0/FN41. HMAC does not make untrusted `joblib` safe. Synthetic ULB-shaped fixture scores are not ULB scores.

## Chapter 12. What this project is—and is not

It is a trilingual FastAPI+HTML/JS **synthetic-only** application and transparent research portfolio: tested scenario generator, logistic model, baselines, local analyst workflow, exports and disclosed limitations. The [benchmark loader](BENCHMARK.md) is separate and optional. It is **not** bank-grade security, real bank integration, proof of customer wrongdoing, a vulnerability scanner, automatic blocking or production deployment. Docker runtime, real public benchmark, shadow evaluation, bias/fairness audit, real feedback, key management and independent security testing were **not done**. The first rule for any future work is not to connect the model to bank decisions without governed data, legal basis, privacy review and human oversight.
