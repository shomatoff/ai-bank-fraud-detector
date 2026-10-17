# Changelog

## Unreleased — v6 local working tree

- Added chronological synthetic event generation and a later-seed test evaluation.
- Added calibrated/logistic model artifacts, validation-only threshold selection, baseline comparisons and model explanations.
- Added local FastAPI dashboard, API validation, analyst reports, audit history and JSON/HTML/PDF/CSV exports.
- Added local artifact hash/HMAC checks, loopback/origin controls, CSRF and local API keys.
- Added i18n completeness, hard-coded-secret and unavailable-model regression tests.
- Added documentation of the deliberate FastAPI + HTML/JavaScript architecture and the current master-prompt gaps.

## v2.0.0 reference

Earlier repository documentation records a v2.0.0 release. The current v6 changes are local working-tree evidence unless a later release URL is explicitly verified; do not infer release publication from this file.

## 2026-10-18 private-repository follow-up

The v6 code/docs audit and a rejected interaction challenger were pushed to private `main` as `d1136ff`. [GitHub Actions run 39065413758](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758) completed successfully (verify and Docker build/health). This is a private code push, **not a new GitHub Release**, bank deployment, or social publication. A stricter unseen-typology gate now requires both no >0.05 absolute recall regression and at least 0.20 recall per synthetic type; the candidate still fails and active v6 remains unchanged.
