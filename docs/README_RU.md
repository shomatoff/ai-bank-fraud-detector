# SentinelAI — локальное руководство v6

Это лаборатория на **синтетических транзакциях**: FastAPI + HTML/JavaScript, не Streamlit. Нет интеграции с банком, настоящих клиентских данных и автоматической блокировки карт/платежей. V6 ещё не опубликована на GitHub. Старые результаты находятся в [архиве](archive/README_RU_V2_V5.md).

**Основной результат (10 seed, новые тестовые seed 400045–400054):** при ровно 5% оповещений precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**; PR-AUC **.7455 [.7219,.7656]**. Скобки — 95% seed-bootstrap интервал, не доверительный интервал эффективности в банке. Парная разница ML минус правило: precision **+.2387 [.2233,.2520]**, recall **+.1923 [.1786,.2045]**. Для невиданного типа `card_testing` recall всего **.0127 [.0025,.0254]**. [Полная оценка](MODEL_EVALUATION.md), [возможности и пределы](FRAUD_DETECTION_CAPABILITIES.md), [карта данных](DATA_CARD.md), [статус бенчмарка](BENCHMARK.md).

В папке проекта на Ubuntu/Python 3.12:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m scripts.v6_evaluation --seeds 10 --rows 12000
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Пока сервер работает, откройте `http://127.0.0.1:8000/` **на своём компьютере**. Для чтения, создания и экспорта отчётов введите локальный analyst-ключ из `data/local-api-keys.json` в поле пароля интерфейса; не делитесь ключом. Подтверждение мошенничества требует admin-ключа, запись также требует CSRF-токена из `/api/config`. Ключ HMAC хранится вне `data/` в файле с правами владельца (`~/.local/share/sentinelai/artifact-signing.key`) либо по пути `SENTINELAI_HMAC_KEY_FILE`; это не банковский корень доверия. [Демо](DEMO_WALKTHROUGH.md), [локальная интеграция](LOCAL_INTEGRATION.md), [дорожная карта](BANKING_INTEGRATION_ROADMAP.md).

Проверки: `.venv/bin/python -m pytest -v`, `.venv/bin/ruff check fraud_detector tests scripts`, `.venv/bin/pip-audit`; для работающего сервера — `.venv/bin/python -m scripts.live_smoke --base http://127.0.0.1:8000`. Docker отсутствует в этой локальной среде; новое CI-задание сборки ещё не выполнялось. Публичного CSV нет: **public benchmark NOT RUN**. Запрошенный реконструированный master prompt отсутствует: [статус gap-анализа](MASTER_PROMPT_GAP_ANALYSIS.md). [Документальная история UZ](PROJECT_DOCUMENTARY_UZ.md) · [EN](PROJECT_DOCUMENTARY_EN.md).
