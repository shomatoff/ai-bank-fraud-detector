# Fraud detection capabilities and limitations — v6-local

This is a **synthetic fraud-monitoring decision-support lab**, not a cybersecurity vulnerability scanner, real-bank integration, customer accusation or automatic payment/card blocker. Current aggregate evaluation is [here](MODEL_EVALUATION.md): exact-5% ten-seed precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**, PR-AUC **.7455 [.7219,.7656]**, with synthetic-seed 95% intervals. Older tables are [archived](archive/FRAUD_DETECTION_CAPABILITIES_V4_V5.md).

## Actual signals and feature provenance

| Model input | Synthetic source / calculation |
|---|---|
| `amount` | Sampled transaction amount; scenario-specific distributions, no real currency or payment |
| `hour` | Hour of timezone-aware simulated event timestamp |
| `merchant_category`, `channel` | Simulated categorical merchant/channel, overridden by scenario behavior |
| `country_risk` | Artificial ordinal level, not a real country or nationality |
| `is_new_device` | Simulated familiarity flag |
| `velocity_1h` | Count of preceding same-customer events in prior 3,600 seconds |
| `distance_km` | Simulated travel distance, no location tracking |
| `account_age_days` | Days since synthetic opening at **event time**; corrected for late new-account episodes |
| `prior_declines_24h` | Count of preceding same-customer declined events in prior 86,400 seconds |

Derived model features are `night = hour<5`, `young_account = account_age_days<90`, and `log_amount = log1p(amount)`. Synthetic ID, event time, scenario, decline status and `is_fraud` are **not** model inputs. The label is a noisy scenario-conditioned Bernoulli draw; see [formula](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md). Historical event windows exclude the current and future events. The frozen hand-rule score uses new device, velocity, declines, transfer, amount, age and country-risk thresholds and was written with generator knowledge; it is **not** an independent fraud-expert baseline. The depth-3 tree baseline is learned on the same fit window.

## Scoring and analyst workflow

The active logistic pipeline outputs a synthetic probability. Validation only chooses regularization, conditional Platt calibration and a default threshold minimizing illustrative `1×FP + 10×FN` under a 10% review cap. Exact test top-k budgets are retrospective ranking comparisons, not live thresholds. The API returns score, threshold, a human-review recommendation, separately labelled hand signals, and exact additive linear contributions to model log-odds. Contributions explain this model's arithmetic, **not causation**, human intent or legally sufficient reasons.

Analysts may create a local synthetic report, move it through `new → in_review → confirmed_fraud/false_positive` (admin key required to confirm), add notes, inspect SQLite audit history, and export JSON/HTML/PDF/CSV. All `/api/reports*` reads, exports and writes require a local analyst/admin API key; writes also require CSRF. Dashboard static pages and health stay open. This is limited local authentication, not production identity or tamper-evident audit. No real transaction can be submitted or blocked by the app.

It may flag patterns resembling the four simulated typologies, but cannot discover arbitrary fraud schemes, prove wrongdoing, scan hosts for cyber vulnerabilities, evaluate real account networks, or infer bank effectiveness. On a larger held-out synthetic stream, unseen card-testing recall was only **.0127 [.0025,.0254]**. False positives burden analysts; false negatives miss labels. Class imbalance, noisy labels, time/episode dependence, imperfect calibration and simulator-specific patterns remain major risks. The 10-seed interval measures only simulator variation, not operational uncertainty. [Banking roadmap](BANKING_INTEGRATION_ROADMAP.md) lists prerequisites that are **not implemented**.
