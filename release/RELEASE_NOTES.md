# SentinelAI v6-local — UNPUBLISHED draft

No v6 tag, GitHub push, release or social post has been made. The primary **synthetic-only** 10-seed result at exact 5% alert volume is precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**, PR-AUC **.7455 [.7219,.7656]** (95% seed-bootstrap intervals). Paired ML-minus-rule differences are precision **+.2387 [.2233,.2520]** and recall **+.1923 [.1786,.2045]**. A dedicated unseen card-testing test had recall **.0127 [.0025,.0254]**. This is not real-bank evidence. V6 spreads all scenarios across time, adds a learned depth-3 baseline, keys all report reads/exports, moves the local HMAC key outside `data/`, and adds a Docker CI job. Real public benchmark and local Docker runtime were **not run**. See [evaluation](../docs/MODEL_EVALUATION.md) and [limitations](../docs/FRAUD_DETECTION_CAPABILITIES.md).

# Historical SentinelAI v2.0.0 — release notes

Scenario event streams, past-only rolling features, chronological evaluation, model/rule/naive baselines, linear non-causal explanations, threshold/cost preview, curves, PSI/slices, strict batch CSV scoring, analyst statuses/audit, JSON/HTML/PDF/CSV exports, model/data cards, Dockerfile and Makefile were added. The dashboard is FastAPI-served HTML/JS, not Streamlit. Final synthetic test: TP167 FP69 FN9 TN2755; precision .707627, recall .948864, PR-AUC .893556. Calibration worsened Brier (.012016→.012800); card-present recall was 0/4. These are not real-bank results.

The source release excludes generated model artifacts and local SQLite reports. Rebuild them with the documented Linux commands.
