# Public-data benchmark — v5 status and reproducible commands

**V6 status: public benchmark NOT RUN.** `data/public/` was absent at the v6 check; no download was attempted. The loader and benchmark pipeline were previously tested only on a **tiny synthetic fixture**, whose historical numbers below are not public-data or bank results. The main FastAPI application still uses only its own synthetic event stream. No public dataset, customer record or model artifact is committed. The earlier unauthenticated Kaggle URL reportedly returned HTTP 404 on 2026-10-15; that event is not independently rerun here. The dataset must be acquired manually from the [ULB/Worldline Kaggle page](https://www.kaggle.com/mlg-ulb/creditcardfraud/) under its displayed terms. Review current terms yourself. Do not enter credentials into this app or commit downloaded data.

The source page describes 284,807 transactions over two days, 492 positives (0.172%), `Time` as elapsed seconds, anonymized PCA `V1`–`V28`, `Amount`, and `Class`. The loader requires exactly those 31 columns and rejects missing/nonfinite values, invalid labels, files over 250 MB, and SHA256 mismatch. `Time` is used only for chronological 60/20/20 fit/validation/test ordering, not as a model input; tie times are kept within one split. The checksum **you** record after a trusted download pins subsequent runs but is not proof of original provenance if the first download is untrusted. No canonical upstream digest was available in this run.

```bash
.venv/bin/python -m pip install -r requirements-benchmark.txt
# Obtain creditcard.csv yourself from the official Kaggle page; do not commit it.
sha256sum data/creditcard.csv
.venv/bin/python -m scripts.run_public_benchmark \
  --csv data/creditcard.csv --sha256 '<the-64-character-digest-you-verified>' \
  --seed 42 --output data/public_benchmark_results.json
```

No public-data metrics are supplied here because that command was **not** run on the canonical CSV. The script fixes the candidate family before test: scaled logistic regression, histogram gradient boosting, optional LightGBM and optional XGBoost if installed. Validation PR-AUC chooses the model, and validation-only `1×FP + 10×FN` under 10% capacity chooses its nominal threshold. The test is scored only after those choices; all candidates are displayed descriptively, with exact retrospective top-k volume 0.5%, 1%, 5%, 10%, actual alert fraction, confusion matrix, precision, recall, F1, FPR and PR-AUC. The always-normal policy has zero alerts and cannot fill a budget. The fixed amount-only rule is intentionally weak; PCA components have no documented semantics to support a richer hand-written fraud rule. The public data have no customer IDs or raw merchant/device data, so this benchmark cannot exercise the local app’s ten feature schema or event-history logic.

Optional SHAP `TreeExplainer` attributes one test row of each compatible tree model; if the package/model combination fails, the result says “SHAP unavailable” with an error type. Logistic contributions are `coefficient × standardized value`. Both are model explanations, not causal or customer-level proof. The feedback demo uses *idealized, perfectly confirmed* labels from the first half of validation, retrains the validation-selected model, chooses before/after thresholds on the later validation half and compares once on the untouched test. It is **not** observed analyst feedback. The same test output should not be used for further tuning.

## Executed synthetic fixture smoke test — not ULB results

Executed 2026-10-15 with Python 3.12.3, scikit-learn 1.9.1, NumPy 2.5.4, pandas 2.3.3, LightGBM 4.7.0, SHAP 0.53.0; XGBoost was not installed. The synthetic ULB-shaped fixture uses seed 273 and 300 rows; split 180/60/60 with seven positives in test. Commands:

```bash
.venv/bin/python -m scripts.make_benchmark_fixture
sha256sum data/tiny-ulb-schema-fixture.csv
.venv/bin/python -m scripts.run_public_benchmark \
  --csv data/tiny-ulb-schema-fixture.csv \
  --sha256 c2039a3074d403232561237ecdb6cfaeec14bf1d92bf1550b2bf17c98ffc401e \
  --seed 42 --output data/fixture_benchmark_results.json
```

Validation selected histogram gradient boosting. On the **60-row synthetic fixture test**, results were:

| Candidate | Test PR-AUC | Exact top 5% alerts | Precision | Recall |
|---|---:|---:|---:|---:|
| Logistic | .134998 | 3/60 (5%) | 0 | 0 |
| Histogram gradient boosting | .152906 | 3/60 (5%) | .333333 | .142857 |
| LightGBM | .140056 | 3/60 (5%) | 0 | 0 |
| Fixed amount rule | .186839 | 3/60 (5%) | 0 | 0 |
| Always normal | .116667 prevalence baseline | 0/60 (0%) | 0 | 0 |

All executed fixture exact-budget rows (confusion order **TP/FP/FN/TN**; actual alert volume shown, including the 0.5% rounding-to-zero limitation):

| Model | Nominal budget / actual alerts | TP/FP/FN/TN | Precision | Recall | F1 | FPR |
|---|---|---|---:|---:|---:|---:|
| Logistic | 0.5% / 0 of 60 (0%) | 0/0/7/53 | 0 | 0 | 0 | 0 |
| Logistic | 1% / 1 of 60 (1.667%) | 0/1/7/52 | 0 | 0 | 0 | .018868 |
| Logistic | 5% / 3 of 60 (5%) | 0/3/7/50 | 0 | 0 | 0 | .056604 |
| Logistic | 10% / 6 of 60 (10%) | 1/5/6/48 | .166667 | .142857 | .153846 | .094340 |
| HGB | 0.5% / 0 of 60 (0%) | 0/0/7/53 | 0 | 0 | 0 | 0 |
| HGB | 1% / 1 of 60 (1.667%) | 0/1/7/52 | 0 | 0 | 0 | .018868 |
| HGB | 5% / 3 of 60 (5%) | 1/2/6/51 | .333333 | .142857 | .200000 | .037736 |
| HGB | 10% / 6 of 60 (10%) | 1/5/6/48 | .166667 | .142857 | .153846 | .094340 |
| LightGBM | 0.5% / 0 of 60 (0%) | 0/0/7/53 | 0 | 0 | 0 | 0 |
| LightGBM | 1% / 1 of 60 (1.667%) | 0/1/7/52 | 0 | 0 | 0 | .018868 |
| LightGBM | 5% / 3 of 60 (5%) | 0/3/7/50 | 0 | 0 | 0 | .056604 |
| LightGBM | 10% / 6 of 60 (10%) | 1/5/6/48 | .166667 | .142857 | .153846 | .094340 |
| Amount rule | 0.5% / 0 of 60 (0%) | 0/0/7/53 | 0 | 0 | 0 | 0 |
| Amount rule | 1% / 1 of 60 (1.667%) | 0/1/7/52 | 0 | 0 | 0 | .018868 |
| Amount rule | 5% / 3 of 60 (5%) | 0/3/7/50 | 0 | 0 | 0 | .056604 |
| Amount rule | 10% / 6 of 60 (10%) | 1/5/6/48 | .166667 | .142857 | .153846 | .094340 |

The always-normal baseline produces 0 alerts (0%) at every budget: TP0 FP0 FN7 TN53, precision/recall/F1/FPR 0 and PR-AUC `.116667`. With just 60 test rows, a 0.5% target rounds to zero and 1% rounds to one alert (1.667% actual); those rows cannot support a useful tiny-budget claim.

In the idealized feedback demo on the same fixture, selected HGB test PR-AUC **fell** from .152906 to .124331; exact-5% TP fell from 1/3 alerts to 0/3. This is tiny, unstable synthetic evidence, not a reason to reject or accept feedback in a bank. LightGBM SHAP emitted an upstream output-shape warning; the code normalizes list/array outputs. No XGBoost results are claimed; the attempted default installation would have downloaded a 305 MB CUDA-related dependency and was stopped, then CPU-oriented LightGBM was installed.

Even a later successful ULB run would not establish bank performance: old anonymized PCA features omit merchant/device/customer semantics, labels can be delayed and selected, base rates shift, and adversaries adapt. See [model evaluation](MODEL_EVALUATION.md), [capabilities](FRAUD_DETECTION_CAPABILITIES.md), and the [banking roadmap](BANKING_INTEGRATION_ROADMAP.md).

## 2026-10-18 source-access follow-up

The official Kaggle dataset page was checked again and still described the 284,807-row, 492-fraud ULB/Worldline CSV. A `curl -L -I` request to Kaggle's unauthenticated `api/v1/datasets/download/mlg-ulb/creditcardfraud` endpoint returned **HTTP 404**; no local Kaggle credentials or canonical CSV were present. No third-party mirror was silently substituted. Therefore the real ULB benchmark remains **NOT RUN**. The model-improvement candidate was instead evaluated only on independent synthetic seeds and rejected by a held-out-typology promotion gate; see [the Uzbek experiment report](AI_CHALLENGER_EVALUATION_UZ.md).
