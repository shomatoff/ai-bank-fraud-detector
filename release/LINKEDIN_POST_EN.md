I built SentinelAI, a local synthetic-only AI bank fraud monitoring portfolio application.

It generates scenario-based synthetic event streams, trains a validation-selected logistic model, evaluates a fresh time-separated test set, and serves an interactive FastAPI HTML/JavaScript dashboard in Uzbek, Russian, and English. It includes model-based linear explanations, rule/naive baselines, threshold-cost preview, diagnostics, analyst audit workflow and local reports.

The important boundary: these are synthetic results. They show how the end-to-end system works, not how it would perform on real bank data. No customer data, banking API, card action, or financial transaction is involved.

Stack: Python, scikit-learn, FastAPI, SQLite, and a responsive JavaScript dashboard. Automated tests and GitHub Actions are included. The final synthetic test was TP167/FP69/FN9/TN2755; precision .7076 and recall .9489. These numbers are not real-bank effectiveness, and no automatic blocking or live payment integration exists.

Repository link: https://github.com/shomatoff/ai-bank-fraud-detector

#MachineLearning #FastAPI #FraudDetection #Python #Portfolio
