# SentinelAI — руководство на русском

Это **локальная лаборатория мониторинга только синтетических транзакций**. Панель — HTML/CSS/JavaScript, обслуживаемые FastAPI, **не Streamlit**. Нет реальных банковских данных, клиентов, платёжных API или автоматической блокировки. [English](../README.md) · [O‘zbek](README_UZ.md).

## Запуск на Linux

Проверенная версия — Python 3.12. Скачайте ZIP из [GitHub репозитория](https://github.com/shomatoff/ai-bank-fraud-detector) или клонируйте его:

```bash
git clone https://github.com/shomatoff/ai-bank-fraud-detector.git
cd ai-bank-fraud-detector
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m pytest -q
.venv/bin/ruff check fraud_detector tests scripts
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Пока сервер работает, откройте `http://127.0.0.1:8000/` **на своём компьютере**. Если порт занят, используйте `--port 8001` и соответствующий адрес. Без работающего процесса локальная ссылка не откроется. Dockerfile/Makefile включены, но выполнение Docker отдельно не подтверждено. Пошаговый процесс — [демо](DEMO_WALKTHROUGH.md).

## Возможности и честные ограничения

Загрузка проекта и пример локального подключения API: [руководство по интеграции](LOCAL_INTEGRATION.md).

Генератор имитирует четыре мошеннических сценария, два сложных законных случая и обычные события; скорость и предыдущие отказы вычисляются только из прошлого того же искусственного клиента. Разделение по времени на обучение/калибровку/валидацию и новый тест, логистическая модель с калибровкой Платта, точные линейные вклады и отдельные описательные правила, базовые методы, графики PR/ROC/надёжности, PSI и сегменты реализованы. Доступны строгая пакетная оценка CSV, локальный процесс `new → in_review → confirmed_fraud/false_positive`, журнал аудита и экспорт JSON/HTML/PDF/CSV. Система лишь предлагает проверку человеком.

В итоговом **синтетическом** тесте 176 меток мошенничества из 3 000 событий: precision .707627, recall .948864, F1 .810680, PR-AUC .893556, ROC AUC .977438, TN2755 FP69 FN9 TP167. Порог .08581994158148241 выбран только на валидации. Калибровка ухудшила тестовую ошибку Brier (.012016 → .012800); в сегменте card-present пропущены 4 из 4 положительных меток. Эти числа **не доказывают эффективность в банке**. Сравнение с v3 не является контролируемым приростом алгоритма: генератор изменился.

Полная таблица статусов TESTED / IMPLEMENTED / PARTIAL / NOT IMPLEMENTED — в [README](../README.md#feature-status). [Аудит возможностей](FRAUD_DETECTION_CAPABILITIES.md) · [фактическая оценка и базовые методы](MODEL_EVALUATION.md) · [подробная формула меток](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md) · [параметры сценариев](SYNTHETIC_SCENARIOS.md) · [карта модели](MODEL_CARD.md) · [карта данных](DATA_CARD.md) · [границы банковской интеграции](BANKING_INTEGRATION_ROADMAP.md) · [демо](DEMO_WALKTHROUGH.md) · [полный отчёт (узбекский)](../IMPLEMENTATION_REPORT_UZ.md) · [реальные скриншоты](../screenshots/README.md).
