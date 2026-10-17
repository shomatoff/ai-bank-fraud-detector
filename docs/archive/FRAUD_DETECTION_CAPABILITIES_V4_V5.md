# Fraud detection capabilities and limitations — v4 audit

**Current v5-local addendum:** The detailed v4 audit below is historical where numbers or security statements differ. The simulator now adds `legit_many_declines`, increases label noise, and uses 60/20/20 fit/calibration/validation plus new test seed 300045. Exact 0.5/1/5/10% retrospective top-k is the primary rule-vs-ML comparison, with validation-threshold alert volumes secondary. Calibration is disabled when validation Brier and ECE fail to improve. Slices with <30 positives show “not evaluable” for recall. Local analyst/admin API keys plus CSRF protect **writes only**; read/report export routes remain unauthenticated on loopback. SHA256 plus local HMAC is checked before `joblib.load`, but the co-located key is not a production trust root. The isolated ULB-schema loader is tested only with a synthetic fixture; public benchmark was NOT RUN. Current exact numbers: [evaluation](MODEL_EVALUATION.md#v5-local-rigor-audit-2026-10-15), [benchmark](BENCHMARK.md), [integration](LOCAL_INTEGRATION.md). No automatic blocking or real-bank connection was added.

## Archived v4 capability audit

Local, synthetic portfolio application only (2026-10-15). Source of truth: [`event_stream.py`](../fraud_detector/event_stream.py), [`features.py`](../fraud_detector/features.py), [`training_v2.py`](../fraud_detector/training_v2.py), [`evaluation.py`](../fraud_detector/evaluation.py), [`api_v2.py`](../fraud_detector/api_v2.py). It is a FastAPI-served HTML/CSS/JavaScript dashboard, **not Streamlit**. No real-bank connection or automatic blocking exists.

## Exact model inputs and provenance

All ten inputs are synthetic or manually entered as *synthetic* examples. The public CSV has exactly these columns and `is_fraud`. Generated `customer_id`, `event_time`, `scenario`, `is_declined` and label are not model inputs. See [scenario parameters](SYNTHETIC_SCENARIOS.md), [data card](DATA_CARD.md), and label explanations [EN](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md) / [UZ](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md) / [RU](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md).

| Input | Synthetic source and calculation |
|---|---|
| `amount` | Base lognormal(4.4,1.08) clipped .01–100,000 artificial units; scenario-specific uniform ranges override it. |
| `hour` | Hour of simulated UTC event time, 0–23. |
| `merchant_category` | Base categorical probabilities .32/.13/.10/.16/.20/.09 for groceries/electronics/travel/fuel/dining/other; typologies override. |
| `channel` | Base card-present .54, online .36, transfer .10; typologies override. |
| `country_risk` | Artificial ordinal 0/1/2 with base .82/.14/.04; selected scenarios force 1–2. Not a real country score. |
| `is_new_device` | Simulated Bernoulli(.08), with scenario overrides; no actual device identifier. |
| `velocity_1h` | Count of **prior** same-customer events in `(time−3600s,time)`, capped at 100; from chronological deque, not drawn independently. |
| `distance_km` | Base exponential(scale34), clipped 0–20,000; scenario-specific ranges override. No real location. |
| `account_age_days` | Customer synthetic starting age 1–20 or 120–2200 plus elapsed simulated days, capped at 36,500. |
| `prior_declines_24h` | Count of **prior** same-customer `is_declined` events in `(time−86400s,time)`, capped at 100. Decline is separately sampled, not fraud label. |

The model derives `night = hour<5`, `young_account = account_age_days<90`, and `log_amount = log1p(amount)`. Categories are one-hot encoded, numeric features standardized using fit data only, and logistic coefficients produce base log-odds. A disjoint calibration sigmoid transforms those logits. These are the only implemented learned predictors; no IP, graph, device fingerprint, geolocation, payee, salary, identity, chargeback or cyber-intelligence features exist.

## Scoring, threshold and explanation

Pydantic rejects missing/out-of-range or extra transaction fields. The calibrated logistic model outputs `P_synthetic`; the fixed default review threshold is .08581994158148241 from validation-only minimization of `FP_cost×FP + FN_cost×FN` (default 1 and 10), capped at 10% validation alert rate. A dashboard preview can change costs/budget or slide a threshold and shows **validation-estimated** volume/precision/recall; it does not re-train or change the saved default. `review_recommended` is a human-review suggestion, not a payment decision. Display level is low below threshold, medium from threshold to below 2×threshold, high otherwise.

The API returns top five **exact model-based linear contributions**: standardized/one-hot feature value × base logistic coefficient × calibration slope, plus an intercept, additive to calibrated log-odds. They explain this *linear score calculation*, not why fraud occurred, data validity, true customer intent, causal effect, or a bank-approved adverse-action reason. Correlated inputs and standardized units complicate intuitive reading. Five separate hand-written display signals (`new_device`, `high_velocity` at ≥4, `country_risk` at ≥1, `prior_declines` at ≥1, `large_amount` at ≥1000) are **not** model attributions. The fixed-rule baseline uses a different explicit formula in [evaluation](MODEL_EVALUATION.md).

## Analyst actions and reporting

An analyst can score one synthetic transaction or a strictly validated UTF-8 CSV batch (exact header, ≤1,000,000 bytes, ≤1,000 rows); inspect curves, PSI and slices; save a SQLite report; move status `new → in_review → confirmed_fraud/false_positive` under the API's allowed transitions; edit a ≤300-character note; inspect local audit history; export a report as JSON, escaped HTML or PDF and export the report list as CSV. There is no assignment, identity/role management, SLA, independent adjudication, irreversible ledger or blocking. Local CSRF, Host/Origin controls, file permissions and artifact hash checks reduce accidental exposure but are **not bank-grade security**; hash is not an authenticated signature, and `joblib` must only load trusted local artifacts. Do not enter private data in analyst notes. Report exports contain submitted synthetic data.

## What this is—and is not

It ranks simulator events that resemble four artificial typologies: account takeover-like activity, card testing, mule/cash-out and new-account high-value transfer, with legitimate travel/large-purchase edge cases. It cannot verify real fraud, identity, coordinated networks, money laundering, account compromise, new tactics or actual customer intent. Fraud monitoring scores financial behavior; cybersecurity vulnerability scanning tests software/hosts/configurations for technical defects. This project does **no vulnerability scan, penetration test, malware detection or credential forensics**.

On the held-out synthetic test, 167 true alerts, 69 false alerts and 9 missed fraud labels occurred at the default threshold (precision .707627, recall .948864). Prevalence was 176/3000 = 5.8667%; always-normal accuracy was 94.1333% while recall was zero. False positives consume analyst time and could harm customers if acted upon; false negatives leave simulated fraud undetected. Small slices can perform much worse (card-present TP0/FN4). The scenario generator supplies both strong feature patterns and noisy labels; apparent performance can be inflated by this coupling. Time splitting and past-only windows reduce future-event leakage, but do not establish external validity. Selection, calibration and threshold use disjoint pre-test data; future tuning on this test would invalidate it. Calibration worsened Brier on this test. No real class-imbalance, bias/fairness, drift or production cost conclusion follows. See [executed evaluation](MODEL_EVALUATION.md) and [roadmap](BANKING_INTEGRATION_ROADMAP.md).
