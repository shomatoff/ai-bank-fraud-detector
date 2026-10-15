# SentinelAI v2.0.0 — draft release notes

Scenario event streams, past-only rolling features, chronological evaluation, model/rule/naive baselines, linear non-causal explanations, threshold/cost preview, curves, PSI/slices, strict batch CSV scoring, analyst statuses/audit, JSON/HTML/PDF/CSV exports, model/data cards, Dockerfile and Makefile were added. The dashboard is FastAPI-served HTML/JS, not Streamlit. Final synthetic test: TP167 FP69 FN9 TN2755; precision .707627, recall .948864, PR-AUC .893556. Calibration worsened Brier (.012016→.012800); card-present recall was 0/4. These are not real-bank results.

The source release excludes generated model artifacts and local SQLite reports. Rebuild them with the documented Linux commands.
