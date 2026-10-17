CODEX MASTER PROMPT — AI Bank Fraud Detector
Project: AI Bank Fraud Detector — Explainable Transaction Risk Analysis Lab
GitHub target: https://github.com/shomatoff/ai-bank-fraud-detector (planned; verify availability)
Author / GitHub: shomatoff
Primary environment: Ubuntu Linux, Python 3.12, local-first
Languages: Uzbek (Latin), Russian, English
Classification: Educational, synthetic-data-only financial fraud detection portfolio project, NOT a live banking system.

YOUR ROLE AND EXECUTION MODE
Act as a senior Python/full-stack engineer, ML engineer, banking fraud analytics practitioner, security engineer, UI/UX designer, QA engineer, and technical documentation writer. Build a genuinely working, verifiable, visually polished portfolio application, rather than a concept, code skeleton or presentation-only demo.
Work systematically and autonomously through local planning, implementation, quality checks, model evaluation, documentation and screenshots. Keep progress summaries short and in Uzbek. Do not stop at a plan. Do not invent tests, metrics, screenshots, downloads or successful actions. Before creating a GitHub repository, pushing commits, creating tags/releases, publishing on LinkedIn, or sending to Telegram, show me a concise verification summary and ask for my approval. If the needed tool/permission is missing, explain the precise limitation and provide commands/next steps; do not bypass consent.
0. VERIFY THE REFERENCE AND ENVIRONMENT
Review the public reference portfolio repositories:
- https://github.com/shomatoff/fim-guard
- https://github.com/shomatoff/linux-security-auditor
- https://github.com/shomatoff/time-manager
Use them ONLY as examples of professional README, screenshots in three languages, CI, releases, honest testing disclosures and documentation quality. Do NOT modify or push to these repos. Inspect their public structure if network is available; otherwise state this and proceed based on requirements below. Confirm that shomatoff/ai-bank-fraud-detector does not already contain a different project before creating it. Work in a new, separate directory; do not alter banking, IRONEYE, GuardBoard or other unrelated projects.
Inventory Python, Git, browser/Playwright, CPU/RAM, available ports and package manager. Choose reliable dependency versions that work on this environment. Make a small phased plan in docs/PLAN.md (not an essay) and execute it. Record obstacles and actual results.
1. PRODUCT SCOPE AND BOUNDARIES
Build an offline-friendly, professional fraud-risk decision-support demonstration for synthetic online banking/card transactions.
Main workflow:
1. Generate a realistic-looking, explicitly SYNTHETIC transaction dataset and keep it reproducible with a fixed seed.
2. Train and evaluate a real machine-learning classifier using correct data splitting and anti-leakage practices.
3. Present transactions and risk assessments in a modern web dashboard.
4. Let an analyst inspect one synthetic transaction, see the risk score, model-supported explanations, related simulated context, and suggested analyst review actions.
5. Allow filtering, trends and exports of synthetic fraud-alert cases.
6. Generate a professional educational review report (HTML plus PDF if available, with a tested fallback).
Never connect to actual banks, card-processing networks, payment rails, real users, live customer records, corporate APIs or internal company systems. Never collect PAN/card numbers, CVV, PIN, passwords, access tokens, real phone numbers, names or addresses. Do not build transaction execution or automatic account/card blocking functionality. Do not claim compliance, production readiness or fraud-prevention guarantees. No actual banking brand marks or claims of endorsement. All demo results must visibly be labeled SYNTHETIC DATA / DEMO.
2. PREFERRED TECHNOLOGY STACK
Keep the MVP maintainable and runnable on one modest Ubuntu laptop, no GPU and no paid cloud APIs:
- Python 3.12
- pandas, numpy
- scikit-learn for genuinely trained ML
- FastAPI, pydantic, uvicorn for REST service
- Streamlit + Plotly for a polished, interactive dashboard
- SQLite for local assessment/history records, if useful (avoid unnecessary complexity)
- joblib to save versioned trained models
- pytest, ruff, GitHub Actions for checks
- HTML/Jinja2 report; add WeasyPrint or ReportLab only when practical and actually tested
- No paid API, external telemetry, unnecessary JavaScript/CDNs, mandatory cloud service, Docker dependence or remote authentication.
Prefer this straightforward architecture. If a dependency is incompatible, document and justify an alternative without expanding scope. Bind backend and UI to 127.0.0.1 by default. Document API versioning and validation. Ensure an offline/local demo runs without any credentials.
3. SYNTHETIC DATA DESIGN
Generate 10,000–30,000 reproducible fake transactions as default, configurable downwards for quick CI. Dataset schema should include:
- opaque synthetic transaction ID and pseudonymous synthetic customer ID
- timestamp (timezone-aware), amount and currency (fake currency code optional)
- merchant category, transaction channel, merchant region
- simulated device familiarity, region change, account age bucket
- past-only velocity features (e.g. transaction attempts in previous hour/day), failed attempt counts
- synthetic fraud label used only for supervised offline training and evaluation
Establish coherent synthetic temporal patterns, imbalanced labels, mundane legitimate activity and challenging examples. Separate ground-truth generation rules from scoring and document any built-in artificial patterns/bias. Do not make a trivial perfect-separation dataset or accidentally leak the label through feature names, future observations, customer identifiers, event IDs or post-event data. Ensure no future events influence prior features. Clearly distinguish model features versus labels and audit-only metadata.
Offer demo dataset generation via an explicit CLI, e.g. python -m fraud_lab.data.generate --rows 20000 --seed 42, with a --help command. No hidden web downloads. The README must explain that learning on synthetic data is NOT validation for real-bank deployment.
4. REAL ML PIPELINE WITH HONEST EVALUATION
Implement:
- A transparent baseline (e.g. logistic regression with a ColumnTransformer: imputation/encoding/scaling inside a persisted pipeline) and optionally compare to one reasonable tree model, without scope explosion.
- Training/validation/test split that respects time; evaluate one chronological untouched test partition. Fit preprocessing on training only. Avoid future-data leakage and entity leakage as applicable; explain tradeoffs.
- Tune an alert threshold on validation only, according to a stated objective; never optimize using the test set.
- Evaluate accuracy only as context, and must report confusion matrix, precision, recall, F1, PR-AUC / average precision, false-positive rate and class prevalence. Include a naive always-legitimate baseline for comparison.
- Show clear rationale for highly imbalanced classes; use class weighting or robust threshold selection as appropriate; do not overclaim performance.
- Version ML artifacts and store non-sensitive metadata: training seed, synthetic data version, threshold, features, library versions, metrics and timestamp. Keep artifact size reasonable. Make retraining explicit, not automatic on each request.
- Inference through one consistent pipeline with strict field validation and informative error handling. Train/test code should reproduce saved model predictions within numeric tolerance.
- Interpretability: where technically faithful, display per-feature contributions from the actual fitted linear model; otherwise display honest global model importance plus labeled illustrative reasons. Do not present arbitrary heuristics as actual ML explanations or causal findings.
- Test edge cases: empty data, one-class sample, missing categories, zero/negative amount, unseen merchant category, NaN, out-of-range numbers, malformed dates, thresholds near boundaries.
Never publish invented F1/accuracy/PR-AUC figures. Compute real metrics, include test set and methodology, and say that synthetic metrics do not reflect operational performance.
5. FASTAPI ENDPOINTS
Implement a minimal, consistent API (names can vary if documented):
- GET /health (does not leak secrets)
- GET /api/v1/summary demo metrics and dataset metadata
- GET /api/v1/transactions with validated pagination/filters
- GET /api/v1/transactions/{id} limited to synthetic transactions
- POST /api/v1/score score one strictly validated synthetic transaction, return risk score, threshold and model version
- GET /api/v1/model-metrics verified metrics and limitations
- GET /api/v1/alerts prioritized flagged transactions
- GET /api/v1/report optional HTML/PDF download if implemented securely
Use typed schemas, safe error messages, bounded page sizes, no arbitrary filesystem access, no token logging, and restrictive CORS/local binding. Add OpenAPI docs. If the API cannot be safely launched, fail visibly rather than showing mock success. Do not expose any API to public internet by default.
6. STREAMLIT DASHBOARD — PREMIUM BANKING SECURITY DESIGN
Visual styling: professional enterprise banking/fraud operations center, not movie-style hacking. Use dark UI by default with accessible typography, contrast and spacing:
- background #0A0E14
- elevated cards #121821
- accent green #00E5A0
- accent blue #4D7CFE
- amber #FFB020
- red #FF4D6A
- primary text #E6EDF3
Tabs/pages:
1. Overview: total synthetic transactions, alert count, alert rate, model status/version, risk distribution, time trends.
2. Transaction explorer: filtering by time/risk/channel/amount, searchable table, pagination.
3. Alert investigation: single transaction view, validated model score, relative evidence/reasons, status new / reviewing / reviewed, analyst notes saved locally.
4. Model performance: validation/test distinctions, honest PR curve/confusion matrix and metric limitations.
5. Reports: downloadable synthetic case summary (HTML/PDF) and CSV/JSON demo alert export.
6. About/methodology: exactly how synthetic data, risk scoring, thresholds and tests work; prominent non-production disclaimer.
Interface must be genuinely interactive and data-driven, not static counters or random values. Use reasonable empty/loading/error states, clear units and accessible controls. Do not imply decisions have been made by a real bank. Risk score is a model output, not a guaranteed probability unless calibration is actually tested and displayed.
7. THREE COMPLETE LANGUAGES — UZ / RU / EN
Translate all UI text, status labels, buttons, alerts, filters, explanations, error messages, report labels and help text into:
- Uzbek (Latin, default)
- Russian
- English
Centralize translation dictionaries; add automated checks that keys exist in all locales. Language selection must persist when practical and not destroy current filters/state. Pay special attention to financial/cybersecurity terminology and Uzbek apostrophes/Cyrillic fonts. README must also be available in 3 languages.
8. REAL SCREENSHOTS, SHORT DEMO AND VISUAL ASSETS
Screenshots must come from a running application, not AI-generated designs, edited mockups or fabricated dashboards. Use synthetic sample transactions. Capture at least:
- docs/screenshots/dashboard-uz.png
- docs/screenshots/dashboard-ru.png
- docs/screenshots/dashboard-en.png
- docs/screenshots/alerts-demo.png
- docs/screenshots/transaction-risk-detail.png
- docs/screenshots/model-performance.png
If a browser automation tool and GUI/browser are available, collect via real browser screenshots and review their readability. If unavailable, clearly mark screenshot tasks as BLOCKED and provide exact commands/manual steps; do not pretend they exist.
Optional, only if feasible: capture a genuine 20–30 second silent screen demo of dashboard -> synthetic suspicious transaction -> explanation -> export using actual running application. Do not synthesize screenshots or narrations and call them app captures. Provide a 30-second storyboard and voiceover script in Uzbek if recording is not possible.
Create source-truthful LinkedIn and Telegram promotional drafts after the application is verified. Static posters may be designed from authentic screenshots, clearly separated from illustrative marketing visuals. Avoid any claim that a real bank uses the application.
9. DOCUMENTATION AND GITHUB PORTFOLIO STANDARD
File layout suggestion (adjust if needed):
ai-bank-fraud-detector/
├── README.md
├── .gitignore
├── .env.example                  # only if truly necessary, no real secrets
├── LICENSE
├── pyproject.toml or requirements.txt
├── fraud_lab/
│   ├── data/
│   ├── ml/
│   ├── api/
│   ├── storage/
│   ├── reporting/
│   └── i18n/
├── dashboard/
├── scripts/
├── tests/
├── docs/
│   ├── README_UZ.md
│   ├── README_RU.md
│   ├── README_EN.md
│   ├── ARCHITECTURE.md
│   ├── DATASET_AND_LIMITATIONS.md
│   ├── MODEL_EVALUATION.md
│   ├── SECURITY.md
│   ├── TESTING.md
│   ├── DEPLOYMENT_LOCAL.md
│   ├── CHANGELOG.md
│   ├── LINKEDIN_POST_EN.md
│   ├── TELEGRAM_POST_UZ.md
│   └── screenshots/
└── .github/workflows/ci.yml
README top section: polished project title, one paragraph in EN/UZ/RU, genuine hero screenshot, link to language-specific detailed guides, real working feature table, install/quick start, synthetic data warning, machine learning methodology/metrics, tests, limitations, GitHub Actions badge and verified release link only when published. Add a short section explaining how this portfolio project relates to financial fraud analytics, but do NOT imply employment endorsement, corporate data use, or real bank integration.
Check all relative links, image URLs and paths. Document Linux and Windows usability only to extent actually tested; avoid unverified cross-platform claims. Commit an MIT license only if appropriate and chosen; no copied proprietary code or banking branding. Ensure no actual customer content in Git history.
10. SECURITY, PRIVACY AND DATA GOVERNANCE
Default to synthetic-only data, local read/write scope and offline use. Log no full transaction payloads when unnecessary. Sanitize exported fields and avoid CSV formula injection (escape dangerous leading characters). Constrain filename/path operations and prevent path traversal. Bound API inputs. Prevent Streamlit from silently calling external services where reasonable, and disclose any network access from dependencies. Avoid leaking local hostnames/usernames in public screenshots. Do not publish machine paths or usernames inside training artifacts. Never call external banking endpoints, send Telegram messages, or automate financial transactions. The real-world use of fraud scoring would require governance, fairness/bias review, privacy/legal review, ongoing monitoring, incident response and human oversight; document this explicitly.
11. TESTING, CI AND RELEASE
Require working automated tests covering at least:
- generator determinism and dataset schema
- timestamps and historical-only velocity
- non-leakage in feature/preprocessing pipeline
- train/validation/test separation and threshold selection
- saved model reload consistency
- risk output bounded and input validation
- metric calculations and class imbalance behavior
- FastAPI health, scoring, invalid inputs, transactions pagination
- i18n completeness in UZ/RU/EN
- CSV/JSON export accuracy and formula safety
- report generation where implemented
- empty and unavailable model states
- privacy: no genuine banking data and no hard-coded secrets
Use pytest -q, ruff check . and a smoke test with the actual running API/dashboard. GitHub Actions should run lint/tests on every push/PR (at minimum Ubuntu Python 3.12), with a reasonable sample dataset for CI. Avoid huge dataset artifacts and paid API dependencies. Document any Windows tests actually run. If GitHub release is approved, use v1.0.0 (unless it already exists), make source/code/docs available and attach only artifacts actually built. Do not label a web dashboard archive a verified desktop installer. Provide a verified SHA256SUMS for published archives only when files exist. Inspect workflow failure logs and fix meaningful failures, not by disabling checks.
12. LINKEDIN AND TELEGRAM PUBLICATION ASSETS
After verified completion create draft files:
- docs/LINKEDIN_POST_EN.md: honest professional English launch post, include tech stack, specific measured demo result with correct caveat, 3-language UI, GitHub/release links only if real, short portfolio learning note and appropriate hashtags.
- docs/TELEGRAM_POST_UZ.md: friendly, short Uzbek channel post for @zerodayuz, explain what AI flags, synthetic demo disclaimer, GitHub link, optional screenshot/video caption.
- docs/SOCIAL_MEDIA_ASSETS.md: instructions for capturing genuine screenshots, recommended 1200x627 or square LinkedIn visuals and 1080x1920 Telegram/Instagram vertical storyboard, with visible DEMO label and no counterfeit data.
Never publish posts without explicit approval, and never falsely say LinkedIn/Telegram is posted if browser/social capabilities are unavailable. If social publishing is impossible, supply complete copy/paste text and image paths.
13. ACCEPTANCE CRITERIA — DO NOT MARK COMPLETE EARLY
- One-command documented local startup (or minimal, reliable two-process startup); basic usage runs fully offline on synthetic data.
- Generated synthetic transactions are reproducible; ML model is fitted and loaded, with an untouched time-based holdout and valid calculated metrics.
- Risk scores/thresholds correspond to the real model, not hard-coded random demo statuses.
- Dashboard main views function; API works with validated requests.
- All three language switches work; docs and screenshots are genuine where present.
- Lint/tests pass, security checks performed, no actual financial data/secrets, no external banking connection.
- README links and downloads resolve and match files actually present.
- GitHub repository/release and social posts only after user approval, with exact success/failure reported.
14. EXECUTION ORDER AND FINAL REPORT
Execute in this order:
1. Inspect current folder and reference repos, avoid overwrites, plan.
2. Create package layout and deterministic synthetic generator.
3. Implement ML train/evaluate/save/load with evidence.
4. Build validated FastAPI endpoints.
5. Create polished Streamlit dashboard and 3-language translations.
6. Add reports/exports and privacy constraints.
7. Write pytest/ruff checks and CI workflow; run and fix.
8. Start the real app; capture genuine screenshots (or clearly state blocker).
9. Finish multilingual README/architecture/evaluation/security docs.
10. Produce LinkedIn and Telegram drafts and truthful marketing/demo assets.
11. Verify all acceptance criteria and show concise Uzbek summary with commands, metrics, test results, screenshot paths and outstanding limits.
12. STOP AND ASK MY APPROVAL before creating/pushing GitHub repo, tags, release and any social publication. If authorized, perform these actions and verify public URLs.
Final report in Uzbek must clearly divide: COMPLETED / TESTED / BLOCKED / NOT DONE. Include precise repo and release URLs only if created; actual measured scores with support and caveats; exact paths for screenshots and post drafts. Never make unverified claims.
BEGIN NOW. Do the real implementation, not only the planning.
