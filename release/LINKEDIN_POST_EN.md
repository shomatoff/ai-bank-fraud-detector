UNPUBLISHED v6 draft — do not post without approval.

I built SentinelAI, a local synthetic-only AI bank fraud monitoring portfolio application.

It generates scenario-based synthetic event streams, trains a validation-selected logistic model, evaluates a fresh time-separated test set, and serves an interactive FastAPI HTML/JavaScript dashboard in Uzbek, Russian, and English. It includes model-based linear explanations, rule/naive baselines, threshold-cost preview, diagnostics, analyst audit workflow and local reports.

The important boundary: these are synthetic results. They show how the end-to-end system works, not how it would perform on real bank data. No customer data, banking API, card action, or financial transaction is involved.

Stack: Python, scikit-learn, FastAPI, SQLite, and a responsive JavaScript dashboard. In the **current v6 local audit**, ten new synthetic test seeds gave mean exact-5%-budget precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**, and PR-AUC **.7455 [.7219,.7656]** (95% seed-bootstrap intervals). The unseen card-testing typology had recall only **.0127 [.0025,.0254]**; that failure matters. These numbers are not real-bank effectiveness. The hand rule was built with generator knowledge, no public CSV benchmark ran, and no automatic blocking or live payment integration exists. V6 is not yet on GitHub.

Repository link: https://github.com/shomatoff/ai-bank-fraud-detector

#MachineLearning #FastAPI #FraudDetection #Python #Portfolio
