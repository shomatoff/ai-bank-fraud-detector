# Evaluation snapshot

The full executed model report is [`docs/MODEL_EVALUATION.md`](docs/MODEL_EVALUATION.md). On 2026-10-15, the independent synthetic v4 test contained 3,000 rows (seed 200045) after chronological fit 7,800, calibration 1,200 and validation 3,000 rows (development seed 42). The validation-selected model was logistic regression; the default threshold was 0.08581994158148241.

| Metric | Executed value |
|---|---:|
| ROC AUC | 0.977438 |
| PR AUC | 0.893556 |
| Precision | 0.707627 |
| Recall | 0.948864 |
| F1 | 0.810680 |
| False-positive rate | 69 / 2,824 = 2.4433% |
| Confusion matrix (TN, FP, FN, TP) | 2,755, 69, 9, 167 |

These are measurements on **artificial** labels, not evidence of real-bank effectiveness. The model misses 9 of 176 synthetic fraud examples; calibration worsened Brier error and card-present recall was 0/4. The v3 numbers were generated under a different simulator and are not a controlled algorithm comparison. No production use is supported.
