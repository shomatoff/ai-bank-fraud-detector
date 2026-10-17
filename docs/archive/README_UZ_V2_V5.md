# SentinelAI — O‘zbekcha qo‘llanma

**Joriy v5-local holat (GitHub’ga yuborilmagan):** yangi sintetik testda precision `.645669`, recall `.867725`, PR-AUC `.796689`; Platt validatsiyada yomonlashgani uchun o‘chirilgan. Hisobot yozish uchun lokal analyst/admin API kaliti va CSRF kerak. 10 seed, exact top-k, ko‘rilmagan tipologiya sinovi hamda public dataset benchmarkining **faqat sintetik fixture** natijalari [v5 baholash](MODEL_EVALUATION.md#v5-local-rigor-audit-2026-10-15) va [benchmark](BENCHMARK.md)da. [Loyiha hujjatli hikoyasi](PROJECT_DOCUMENTARY_UZ.md) · [English documentary](PROJECT_DOCUMENTARY_EN.md). Quyidagi eski `.707627/.948864` raqamlar v2.0.0 tarixiy holatidir, joriy natija emas.

Bu **faqat sintetik ma’lumotli lokal** firibgarlik monitoring laboratoriyasi. Dashboard FastAPI taqdim etadigan HTML/CSS/JavaScript; Streamlit emas. Haqiqiy bank yozuvi, mijoz ma’lumoti, jonli to‘lov API va avtomatik bloklash yo‘q. [English](../README.md) · [Русский](README_RU.md).

## Linuxda ishga tushirish

Tekshirilgan versiya Python 3.12. [GitHub repository](https://github.com/shomatoff/ai-bank-fraud-detector) ZIP faylini yuklab oching yoki quyidagicha clone qiling:

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

Terminal ochiq turganda `http://127.0.0.1:8000/` ni **o‘z kompyuteringizda** oching. 8000 band bo‘lsa `--port 8001` va mos havolani ishlating. Server to‘xtagan bo‘lsa 127.0.0.1 havolasi ochilmaydi. Dockerfile va Makefile mavjud; Docker ishga tushishi ushbu hisobotda alohida tekshirilmagan. To‘liq amaliy jarayon [demo](DEMO_WALKTHROUGH.md)da.

## Nima ishlaydi va nimaga ishonmaslik kerak

Yuklab olish va lokal API orqali ulash namunasi: [integratsiya qo‘llanmasi](LOCAL_INTEGRATION.md).

To‘rtta firibgarlikka o‘xshash ssenariy, ikki qonuniy murakkab holat va normal voqealardan sintetik vaqt oqimi yaratiladi. `velocity_1h` va `prior_declines_24h` faqat oldingi voqealardan hisoblanadi. Vaqt bo‘yicha o‘qitish/kalibrlash/validatsiya va yangi urug‘li test ajratiladi. Logistik model, Platt kalibrlash, besh chiziqli model hissasi va alohida tavsifiy signallar, qoidaviy baseline, PR/ROC/ishonchlilik grafiklari, PSI va guruhlar tahlili mavjud. CSV partiyasini baholash, SQLite’dagi `new → in_review → confirmed_fraud/false_positive` jarayoni, audit hamda JSON/HTML/PDF/CSV eksport ishlaydi. Faqat inson ko‘rigi tavsiya qilinadi.

Yakuniy **sintetik** testda 3 000 voqeadan 176 tasi yorliqda firibgarlik: precision .707627, recall .948864, F1 .810680, PR-AUC .893556, ROC AUC .977438; TN2755 FP69 FN9 TP167. Chegara .08581994158148241 faqat validatsiyada tanlangan. Kalibrlash test Brier xatosini yaxshilamadi (.012016 → .012800). Card-present guruhida 4/4 fraud o‘tkazib yuborilgan. Bu raqamlar real bank samaradorligini **isbotlamaydi**. Eski v3 raqamlari bilan farq asosan generator o‘zgargan sharoitda olingan, algoritmning nazoratli yutug‘i emas.

To‘liq imkoniyat holati (TESTED / IMPLEMENTED / PARTIAL / NOT IMPLEMENTED) [asosiy README jadvali](../README.md#feature-status)da. [Imkoniyat va cheklovlar auditi](FRAUD_DETECTION_CAPABILITIES.md) · [haqiqiy baholash va baseline](MODEL_EVALUATION.md) · [yorliq formulasi, qadam-baqadam](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md) · [ssenariy parametrlari](SYNTHETIC_SCENARIOS.md) · [model kartasi](MODEL_CARD.md) · [ma’lumot kartasi](DATA_CARD.md) · [bank integratsiyasi chegaralari](BANKING_INTEGRATION_ROADMAP.md) · [demo](DEMO_WALKTHROUGH.md) · [to‘liq ish hisoboti](../IMPLEMENTATION_REPORT_UZ.md) · [haqiqiy skrinshotlar](../screenshots/README.md).
