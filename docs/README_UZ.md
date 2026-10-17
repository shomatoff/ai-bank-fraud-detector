# SentinelAI — v6 lokal qo‘llanma

Bu faqat **sintetik tranzaksiyalar** bilan ishlaydigan FastAPI + HTML/JavaScript tahlil laboratoriyasi; Streamlit, haqiqiy bank integratsiyasi va avtomatik karta/to‘lov bloklashi yo‘q. V6 kodi private GitHub reposiga yuborilgan, lekin bu model bankda ishlashga tayyor degani emas. Eski natijalar [arxivda](archive/README_UZ_V2_V5.md).

Dashboardda 8 ko‘rinish bor: Umumiy ko‘rinish, Tranzaksiyalar, Risk tahlili, Hisobotlar, Model natijalari, Tekshiruv navbati, Operatsiyalar va Imkoniyatlar. Navbat qat’iy sintetik namunani model bahosi bo‘yicha saralaydi; card-testing ishorasi tartibni o‘zgartirmaydi. Operatsiyalar sahifasidagi alertlar 1000 qatorlik demo namunadan, drift ko‘rsatkichlari esa tarixiy sintetik validatsiyadan — ular jonli bank telemetriyasi emas. Feedback xulosasi faqat lokal admin kaliti bilan ochiladi; yangi sahifa kalitni saqlamaydi va foydalanishdan keyin maydonni bo‘shatadi. Imkoniyatlar sahifasida lokal ishlaydigan, alohida tadqiqotdagi va mavjud bo‘lmagan qismlar ajratilgan. Ishlayotgan lokal serverda `APP_PORT=8000 node scripts/dashboard_smoke.mjs` orqali Chrome’da uch til, navbat, feedback va mobil layout tekshiriladi.

**Asosiy natija (10 seed, yangi test seedlari 400045–400054):** aynan 5% alert hajmida precision **.8313 [.8147,.8487]**, recall **.6689 [.6566,.6799]**; PR-AUC **.7455 [.7219,.7656]**. Qavslar 95% seed-bootstrap intervali, haqiqiy bank ishonch oralig‘i emas. Qoida/ML juft farqi: precision **+.2387 [.2233,.2520]**, recall **+.1923 [.1786,.2045]**. Ko‘rilmagan `card_testing` tipologiyasida recall **.0127 [.0025,.0254]** — jiddiy cheklov. [To‘liq baholash](MODEL_EVALUATION.md), [imkoniyatlar](FRAUD_DETECTION_CAPABILITIES.md), [data card](DATA_CARD.md), [benchmark holati](BENCHMARK.md).

Ubuntu/Python 3.12 da loyiha papkasidan:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m scripts.v6_evaluation --seeds 10 --rows 12000
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Server ishlayotgan paytda **o‘z kompyuteringizda** `http://127.0.0.1:8000/` ni oching. Analitik hisobotlarini o‘qish, yozish va eksport qilish uchun lokal `data/local-api-keys.json`dagi analyst kalitini UI’ning password maydoniga kiriting; kalitni hech kimga yubormang. Tasdiqlangan firibgarlik holati uchun admin kaliti kerak. Yozishda `/api/config`dan CSRF token ham talab qilinadi. HMAC kaliti `data/`dan tashqaridagi owner-only faylda (`~/.local/share/sentinelai/artifact-signing.key`) yoki `SENTINELAI_HMAC_KEY_FILE` yo‘lida turadi; bu bank darajasidagi trust root emas. JSON/HTML/PDF/CSV hisobotlar faqat sintetik ma’lumot uchun. [Demo yurishi](DEMO_WALKTHROUGH.md), [lokal integratsiya](LOCAL_INTEGRATION.md), [roadmap](BANKING_INTEGRATION_ROADMAP.md).

Tekshiruv: `.venv/bin/python -m pytest -v`, `.venv/bin/ruff check fraud_detector tests scripts`, `.venv/bin/pip-audit`; ishlayotgan serverga `.venv/bin/python -m scripts.live_smoke --base http://127.0.0.1:8000`. Docker bu mahalliy muhitda yo‘q, private GitHub CI’da build/start/health tekshirilgan. Rasmiy Kaggle ULB v3 CSV alohida benchmarkda ishlatilgan, lekin uning modeli ushbu ilovaga ulanmagan: [benchmark holati](BENCHMARK.md). Asl master prompt topilmagan: [gap holati](MASTER_PROMPT_GAP_ANALYSIS.md). [O‘zbek hujjatli tarix](PROJECT_DOCUMENTARY_UZ.md) · [English documentary](PROJECT_DOCUMENTARY_EN.md).
