# Model evaluation — current v6-local synthetic audit

**Primary result:** 10 independent development seeds 42–51, each with a new later test seed 400045–400054. At **exactly 5%** retrospective alert volume (150 of 3,000 per test), logistic ML precision is **0.8313 [0.8147, 0.8487]**, recall **0.6689 [0.6566, 0.6799]**, and test PR-AUC **0.7455 [0.7219, 0.7656]**. Brackets are 95% percentile bootstrap intervals over the ten seed-level results (10,000 resamples, bootstrap seed 518), *not* a bank-performance confidence interval. Synthetic labels are not verified customer wrongdoing. Full per-seed JSON and execution output: `data/v6_evaluation.json` (local, ignored) and `verification_bundle/v6_evaluation.txt`. Reproduce with `.venv/bin/python -m scripts.v6_evaluation --seeds 10 --rows 12000 --heldout-rows 30000`.

Each seed generates 12,000 January development events: first 7,200 fit, next 2,400 disjoint calibration, final 2,400 validation. The test is a separately generated 3,000-row March stream. Model regularization, optional Platt use and cost-constrained threshold are chosen without test labels. Past-only velocity/declines are computed chronologically; scenario, synthetic customer ID, time and label are not model inputs. The **new-account fraud episodes are spread over the full simulated month**, and account age is evaluated relative to each account's opening time. The generator test asserts at least 10 events of every scenario in each fit/calibration/validation/test window at default sizes. This corrects the v5 early-window bias, but does not eliminate simulator coupling or customer/episode dependence.

## Exact top-k comparison — ten-seed means [95% seed-bootstrap CI]

All three methods rank the **same** synthetic test rows; actual alerts are 15/30/150/300 of 3,000 at 0.5/1/5/10%. Exact top-k requires the full score batch and is **not** a live deployable threshold. The fixed hand rule was written with knowledge of this generator; it is not an independent baseline. A depth-3 decision tree is fit on the same fit window as logistic ML. An independent human review of the hand rule is still recommended.

| Budget | Model | Precision | Recall |
|---|---|---:|---:|
| 0.5% | Fixed rule | .5467 [.5000,.5933] | .0440 [.0402,.0477] |
| 0.5% | Depth-3 tree | .8400 [.8000,.8800] | .0678 [.0637,.0718] |
| 0.5% | Logistic ML | .8600 [.7933,.9133] | .0693 [.0634,.0745] |
| 1% | Fixed rule | .7067 [.6867,.7300] | .1138 [.1103,.1176] |
| 1% | Depth-3 tree | .8300 [.8133,.8500] | .1337 [.1292,.1381] |
| 1% | Logistic ML | .8667 [.8067,.9067] | .1396 [.1297,.1473] |
| 5% | Fixed rule | .5927 [.5740,.6087] | .4766 [.4669,.4855] |
| 5% | Depth-3 tree | .7447 [.7233,.7680] | .5991 [.5845,.6143] |
| 5% | Logistic ML | .8313 [.8147,.8487] | .6689 [.6566,.6799] |
| 10% | Fixed rule | .4663 [.4580,.4753] | .7506 [.7359,.7649] |
| 10% | Depth-3 tree | .4677 [.4547,.4797] | .7533 [.7253,.7787] |
| 10% | Logistic ML | .5333 [.5250,.5427] | .8584 [.8439,.8696] |

Paired **ML minus fixed rule** differences, bootstrap resampling the ten paired seed-level differences:

| Budget | Precision difference [95% CI] | Recall difference [95% CI] |
|---|---:|---:|
| 0.5% | +.3133 [.2067,.4000] | +.0253 [.0166,.0326] |
| 1% | +.1600 [.0867,.2100] | +.0258 [.0138,.0340] |
| 5% | +.2387 [.2233,.2520] | +.1923 [.1786,.2045] |
| 10% | +.0670 [.0590,.0747] | +.1078 [.0949,.1198] |

The always-normal baseline flags **zero** rows at every budget: precision/recall/F1/FPR = 0, with PR-AUC equal to each test's prevalence; it does not artificially fill a quota. Full F1, FPR, confusion matrices, nominal validation-derived thresholds and **actual** flagged fractions for each method/seed are in the execution output. Nominal thresholds are secondary because a validation quota need not produce the same test alert rate.

## Label-noise and capacity limits

The four fraud typologies draw positive labels with `p=.88`; normal events draw .01 and `legit_many_declines` .02. If a ranking selected *only* those fraud-typology events, its **expected** precision would be about .88. This is *not* a deterministic finite-sample upper bound: random draws and mixed scenario selection can make observed precision higher or lower. At exact k, recall is arithmetically at most `min(1, k / test_positives)` regardless of model. Across these ten tests the mean arithmetic recall ceiling is .0805 at 0.5%, .1610 at 1%, .8052 at 5%, and 1.0000 at 10%; each seed's ceiling is printed beside its metrics in the output. These constraints expose artificial-label difficulty; they are not evidence of real fraud detection.

## Calibration and one labelled example

Platt was enabled by validation Brier **and** 10-bin ECE for seeds **42,43,44,46,49,50,51** and disabled for **45,47,48**. A separate forced-off run was executed for every seed. Forced-off exact-5% precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**, and PR-AUC **.7455 [.7219,.7656]** match the conditional-calibration results because Platt's fitted sigmoid preserved score ranking here; probability calibration, Brier and nominal thresholds need not match. The per-seed decision is printed in `v6_evaluation.txt`.

**Seed 42 only, not a headline:** test seed 400045 has 3,000 rows, 184 positives. Validation chose threshold `.20284049321690387`; default-threshold confusion is TN2749/FP67/FN32/TP152, precision `.694064`, recall `.826087`, PR-AUC `.757606`, ROC AUC `.927837`, Brier `.023250`. At exact 5%, ML TP126/FP24/FN58/TN2792 (precision .8400, recall .6848), rule TP92/FP58/FN92/TN2758, tree TP111/FP39/FN73/TN2777. These single-seed values are **examples only**.

## Held-out fraud typologies

For each row, its named type was removed from fit **and** validation. Model selection and threshold use known types on validation only. A separate **30,000-row** May stream with seed **900045** contains 450 events of each held-out type and at least 200 positive labels. The 95% interval bootstraps positive **rows**, not independent customer/episode clusters, so it can be optimistic.

| Withheld type | Positives | TP / FN | Recall [95% positive-row bootstrap CI] |
|---|---:|---:|---:|
| Account takeover | 401 | 297 / 104 | .7406 [.6983,.7830] |
| Card testing | 393 | 5 / 388 | **.0127 [.0025,.0254]** |
| Mule / cash-out | 392 | 344 / 48 | .8776 [.8444,.9082] |
| New-account transfer | 396 | 271 / 125 | .6843 [.6389,.7298] |

The near-zero unseen card-testing recall is a serious simulator-level failure. It does not justify deployment or an inference about real cards. Subgroup recall elsewhere is marked **not evaluable** when fewer than 30 positives; no fairness conclusion is drawn.

## Historical results and boundaries

**Historical v5 (different generator and test seeds):** exact-5% ten-seed precision .813333 [.800667,.828667], recall .661446 [.648752,.674807], PR-AUC .731488 [.715733,.750300]. The v6 changes were not a controlled algorithm-only A/B test. Earlier v2/v3/v4 tables and the full v5 evaluation were moved to [the archive](archive/MODEL_EVALUATION_V2_V5.md); none is the current headline. Synthetic accuracy, even with confidence intervals, cannot establish real-bank effectiveness. No real/public CSV benchmark ran in v6 because `data/public/` was absent. No automatic transaction blocking or real-bank integration exists.
