# Executed model evaluation — synthetic-only v4

Run: 2026-10-15, `.venv/bin/python -m fraud_detector.model`; source of exact values: regenerated local `data/metrics.json`. This documents executed results, **not real-bank effectiveness**. The v4 model was selected/thresholded before its March synthetic test labels were examined; later addition of retrospective top-k reporting did not alter that model or threshold. Any future tuning informed by this test requires a *new* untouched test.

## Design and leakage controls

The seeded customer event stream is chronological. January development (`seed=42`, 12,000 rows) was cut by time into fit 7,800 (65%), calibration 1,200 (10%), and validation 3,000 (25%). March test (`seed=200045`, 3,000 rows) is freshly generated, later in simulated time, and held out from fitting, calibration, model choice and default threshold choice. Fraud counts/rates: fit 566/7,800 = 7.2564%; calibration 50/1,200 = 4.1667%; validation 116/3,000 = 3.8667%; test 176/3,000 = 5.8667%. The time-rate mismatch is a simulator limitation.

The two predeclared logistic candidates had validation PR-AUC 0.76911196 (`C=1`) and 0.76663714 (`C=.25`); `C=1` won. Fitted one-hot/scaler parameters see fit rows only. Platt calibration uses only the disjoint calibration slice. The default threshold minimizes `1×FP + 10×FN` on validation while limiting validation alerts to at most 10%, yielding **0.08581994158148241**. On validation it alerted 157/3,000 (5.2333%), with TP96 FP61 FN20 TN2823, precision .611465 and recall .827586. The cost weights are illustrative and editable in the dashboard, not bank loss estimates.

`velocity_1h` and `prior_declines_24h` use only preceding same-customer events; the current event and label are excluded. Scenario, synthetic customer ID, timestamp, decline flag and target are never scoring features. Nonetheless feature/label distribution comes from one easy simulator, so there is severe *generator coupling* even with no row-level future leakage. [Data card](DATA_CARD.md), [scenarios](SYNTHETIC_SCENARIOS.md).

## Final test at validation-selected default policy

| Metric | Executed result |
|---|---:|
| Fraud prevalence | 176/3,000 = 5.8667% |
| Alerts | 236/3,000 = 7.8667% |
| Precision | 167/236 = 0.707627 |
| Recall | 167/176 = 0.948864 |
| F1 | 0.810680 |
| PR-AUC / average precision | 0.893556 |
| ROC AUC | 0.977438 |
| False-positive rate | 69/2,824 = 0.024433 |
| Brier, calibrated | 0.012800 |
| Brier, raw before Platt | 0.012016 — **better than calibrated** |

| Actual / predicted | Normal | Alert |
|---|---:|---:|
| Normal | TN 2,755 | FP 69 |
| Fraud | FN 9 | TP 167 |

Thus 9 simulator fraud labels were missed and 69 simulator normal labels created review workload. Platt was implemented but **did not improve Brier on this test**. The reliability, PR and ROC curves in the dashboard are test diagnostics, not selection inputs. The high metrics reflect especially distinctive artificial scenarios and are not comparable as an algorithm-only improvement over the old generator.

## Baselines and equal alert-budget comparisons

Always-normal has zero alerts, TP0 FP0 FN176 TN2824, precision/recall/F1/FPR 0, PR-AUC equal to prevalence .058667 and ROC AUC .5. It has 94.1333% accuracy while detecting nothing. A frozen hand-written score adds 2 for new device, 1.5 each for velocity≥3, prior decline≥1 and transfer, 1 for amount≥1200 and age<90 days, 0.5 for country risk≥1, plus min(amount/100000,.1). It was not fitted on test labels. Fixed-rule PR-AUC is .750108, ROC AUC .970813; ML PR-AUC .893556, ROC AUC .977438. Rule score is not a probability; no Brier is assigned.

Thresholds fixed from **validation** at nominal budgets; actual test volumes drift:

| Policy / nominal budget | Test alerts | TP/FP/FN/TN | Precision | Recall | F1 | FPR |
|---|---:|---|---:|---:|---:|---:|
| Always normal / 5% or 10% | 0 | 0/0/176/2824 | 0 | 0 | 0 | 0 |
| Rules / 5% | 219 (7.3%) | 147/72/29/2752 | .671233 | .835227 | .744304 | .025496 |
| ML / 5% | 232 (7.733%) | 167/65/9/2759 | .719828 | .948864 | .818627 | .023017 |
| Rules / 10% | 372 (12.4%) | 165/207/11/2617 | .443548 | .937500 | .602190 | .073300 |
| ML / 10% | 353 (11.767%) | 169/184/7/2640 | .478754 | .960227 | .638941 | .065156 |

For a strictly **same realized test volume**, the following *retrospective* ranking selects the highest test scores without looking at test labels. This is a descriptive offline comparison, **not a deployable threshold**, because the full batch score distribution is needed:

| Budget / model | Alerts | TP/FP/FN/TN | Precision | Recall | F1 | FPR |
|---|---:|---|---:|---:|---:|---:|
| 5% / rules | 150 | 106/44/70/2780 | .706667 | .602273 | .650307 | .015581 |
| 5% / ML | 150 | 138/12/38/2812 | .920000 | .784091 | .846626 | .004249 |
| 10% / rules | 300 | 160/140/16/2684 | .533333 | .909091 | .672269 | .049575 |
| 10% / ML | 300 | 169/131/7/2693 | .563333 | .960227 | .710084 | .046388 |

The always-normal policy remains at zero alerts and cannot fill an alert budget meaningfully. No threshold was retuned on test labels.

## Monitoring and limitations

Amount PSI between validation and test is .008654; deliberately multiplying test amounts by 1.5 yields .141876. These are descriptive synthetic examples, not a universal drift alarm. Per-slice metrics are generated for channel, artificial `country_risk`, and account age; the **card-present slice has 0/4 fraud labels recovered**, despite high aggregate recall. Four positives are too few to generalize, but this failure must not be hidden. Country-risk is not a real country or fairness proxy.

Synthetic accuracy cannot establish operational effectiveness: real base rates, delayed labels, adversarial adaptation, false-alarm cost, customer harm, distributions, legal/privacy constraints, and temporal drift differ. This project contains no bank-grade security certification, production validation, real-world calibration, prospective shadow trial or external fairness study. See [capabilities](FRAUD_DETECTION_CAPABILITIES.md), [model card](MODEL_CARD.md), and [integration roadmap](BANKING_INTEGRATION_ROADMAP.md).
