# Executed model evaluation — synthetic-only v4

**Historical v2.0.0 result below. Current v5-local evaluation is in the [v5 section](#v5-local-rigor-audit-2026-10-15) at the end; do not apply v4 numbers to current code.**

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

## v5-local rigor audit (2026-10-15)

Executed `.venv/bin/python -m fraud_detector.model` after changing the simulator and split. Development seed 42: chronological fit 7,200 (60%), calibration 2,400 (20%), validation 2,400 (20%); later independent **new test seed 300045**: 3,000 rows, 189 positives (6.3%). This v5 seed was chosen after detecting accidental reuse of v2's 200045 test seed; the intermediate reused-seed result was not used for model tuning and is described in the [documentary](PROJECT_DOCUMENTARY_EN.md). Candidate C=1 won validation; validation-only cost/cap policy chose threshold `.18489421127174294`. The new test yielded TN2721 FP90 FN25 TP164, alerts 254/3000 (8.4667%), precision `.645669`, recall `.867725`, F1 `.740406`, FPR `.032017`, PR-AUC `.796689`, ROC AUC `.934317`. V2/v4 test precision `.707627`, recall `.948864`, PR-AUC `.893556`; the decrease is observed, but altered labels, edge cases, split and test seed prevent causal attribution to one change.

### Primary: exact same realized alert volume

This retrospective top-k view selects the highest *unlabeled* test scores within each full batch. It is fair for offline ranking and uses no test labels for cutoff selection, but is **not** a deployable streaming threshold. `always_normal` has zero alerts, not forced meaningless random alerts. PR-AUC does not depend on the budget: v5 ML `.796689`, fixed rules `.557977`, always-normal `.063000` (prevalence).

| Budget / actual flagged | Method | TP/FP/FN/TN | Precision | Recall | F1 | FPR |
|---|---|---|---:|---:|---:|---:|
| 0.5% / 15 of 3000 | Rules | 9/6/180/2805 | .600000 | .047619 | .088235 | .002134 |
| 0.5% / 15 of 3000 | ML | 13/2/176/2809 | .866667 | .068783 | .127451 | .000711 |
| 1% / 30 of 3000 | Rules | 20/10/169/2801 | .666667 | .105820 | .182648 | .003557 |
| 1% / 30 of 3000 | ML | 26/4/163/2807 | .866667 | .137566 | .237443 | .001423 |
| 5% / 150 of 3000 | Rules | 91/59/98/2752 | .606667 | .481481 | .536873 | .020989 |
| 5% / 150 of 3000 | ML | 130/20/59/2791 | .866667 | .687831 | .766962 | .007115 |
| 10% / 300 of 3000 | Rules | 153/147/36/2664 | .510000 | .809524 | .625767 | .052295 |
| 10% / 300 of 3000 | ML | 165/135/24/2676 | .550000 | .873016 | .674847 | .048026 |

Full F1/FPR for every row are in reproducibly generated `data/metrics.json` under `comparison.*.exact_test_top_k`. Always-normal: TP0 FP0 FN189 TN2811, 0/3000 alerts (0%), precision/recall/F1/FPR 0, PR-AUC equal to prevalence `.063`.

### Secondary: validation-derived nominal thresholds

These are operationally selectable cutoffs, **not** exact test capacity. Actual flagged percentages are shown on every row. The legacy JSON key `ml_calibrated` names the selected model even when v5 disables calibration; inspect `calibration_method`.

| Nominal budget | Rule actual alerts | Rule precision / recall | ML actual alerts | ML precision / recall |
|---|---:|---|---:|---|
| 0.5% | 51/3000 (1.7000%) | .764706 / .206349 | 35/3000 (1.1667%) | .885714 / .164021 |
| 1% | 77/3000 (2.5667%) | .701299 / .285714 | 76/3000 (2.5333%) | .934211 / .375661 |
| 5% | 238/3000 (7.9333%) | .533613 / .671958 | 252/3000 (8.4000%) | .650794 / .867725 |
| 10% | 416/3000 (13.8667%) | .396635 / .873016 | 406/3000 (13.5333%) | .411330 / .883598 |

Platt calibration was fitted on a doubled, disjoint 20% calibration split and enabled only if **both** validation Brier and equal-width 10-bin ECE improved. They did not: raw Brier `.017899` vs Platt `.018520`; raw ECE `.014630` vs Platt `.018282`. Thus v5 serves the raw logistic probability. Its **new test** Brier is `.021669`. ECE is sample- and bin-sensitive. No calibration choice used test labels.

Card-present has 14 positives and TP0/14 at the default threshold: recorded confusion matrix, but **recall is shown as “not evaluable (<30 positives)”** in the dashboard/API rather than a generalized subgroup estimate. The generator was not artificially changed simply to make this slice look stable. Online has 91 positives and 80 TP; transfer 84 positives and 84 TP. This gap remains serious, not a fairness conclusion.

### Repetition, uncertainty and unseen fraud types

Executed `.venv/bin/python -m scripts.v5_evaluation --seeds 10 --rows 12000` for independent development seeds 42–51 and **new** test seeds 300045–300054. Ten *whole-pipeline* runs each retrained, chose C, decided whether to calibrate and chose a threshold on its own validation. For exact-5% ranking across the ten later synthetic tests, unweighted seed means and 95% percentile bootstrap intervals (10,000 seed-level resamples, bootstrap seed 518) were: precision `.813333` [.800667, .828667], recall `.661446` [.648752, .674807], PR-AUC `.731488` [.715733, .750300]. This interval measures only seed-to-seed simulator variation; it is not a real-bank confidence interval. Exact per-seed values are reproducible in `data/v5_evaluation.json` (generated, not committed).

The separate seed-42 held-out-typology audit removed each type from fit **and validation** and evaluated that type in the independent later test; its threshold came from validation containing only known types. Account takeover: TP23/FN16, recall .589744 (39 positives). Card testing: **TP0/FN41, recall 0** (41 positives). Mule/cash-out: TP40/FN1, recall .975610 (41 positives). New-account transfer: TP24/FN19, recall .558140 (43 positives). This is a strong counterexample to assuming good aggregate recall transfers to novel schemes. Each test scenario has only 45 rows and simulator-specific structure.

The v5 ambiguity case `legit_many_declines` (2.5% planned share) has 85% decline probability but only 2% positive-label probability; normal positive noise rose `.005→.01`, fraud scenario positive probability fell `.94→.88`. These changes and split changes coincided with lower metrics; no controlled ablation was run to assign the drop to one parameter. The [public benchmark](BENCHMARK.md) has **no actual public-data run**, and synthetic test accuracy remains no evidence of bank effectiveness.
