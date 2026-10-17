# SentinelAI: 0 dan 100 gacha — dalillarga tayangan hujjatli hikoya

Bu matn badiiylashtirilgan sarlavhali **texnik xronika**, suhbat yoki sahna voqealari to‘qib chiqarilmagan. Manbalar: Git tarixidagi `4da0fb3`, `07b05da`, `0babd0d`; [v2 hisobot](../IMPLEMENTATION_REPORT_UZ.md)ning v5 qo‘shimchasidan **oldingi** qismi; [v4 baholash](MODEL_EVALUATION.md); joriy `fraud_detector/`, `tests/`, `scripts/` va v5 bajarilgan chiqishlari. Ilk prototiplarning commitlari ushbu repozitoriy tarixida yo‘q — ularning aniq sanasi va har bir qadam logi **qayd etilmagan**. Bu ishda “100” mahsulot yetukligi yoki bank uchun tayyorlik emas, hikoya yakuni.

## 1-bob. G‘oya: bankni emas, xavfsiz laboratoriyani kuzatish

Kadrda talab aniq: haqiqiy bank yozuvi, mijoz, credential, jonli to‘lov API va avtomatik bloklash yo‘q. `README.md`, `docs/BANKING_INTEGRATION_ROADMAP.md` va `fraud_detector/api_v2.py` faqat lokal sintetik monitoringni ta’riflaydi. Veb interfeys Streamlit emas: FastAPI `web/index.html`, CSS va JavaScript’ni taqdim etadi. Dastlabki master prompt fayli workspace/Desktop qidiruvida topilmagani [v2 hisobotda](../IMPLEMENTATION_REPORT_UZ.md) qayd qilingan; mazmuni va bajarilish foizini tekshirish mumkin emas.

## 2-bob. Ish maydoni: Python, test va chegaralar

Kod `fraud_detector/`, `web/`, `scripts/`, `tests/`, `docs/`ga ajratilgan; virtual muhit `.venv`da. Python 3.12, FastAPI, scikit-learn, NumPy/pandas, SQLite, HTML/CSS/JS, pytest, Ruff, pip-audit va Chrome CDP ishlatilgani v2 hisobot va `requirements*.txt`/`scripts/capture.mjs`da ko‘rinadi. Birinchi lokal papka qachon yaratilgani **qayd etilmagan**. `Dockerfile` va `Makefile` bor, lekin v5 `docker build -t sentinelai-v5-local .` chiqishi `/bin/bash: docker: command not found` (exit 127); image ishladi deyish mumkin emas.

## 3-bob. Ilk generator va ilk model: ko‘rsatkichga ishonmaslik sabog‘i

Oldingi v3 yorliq mexanizmi `Bernoulli(sigmoid(z))` bo‘lgan; bu tarix [yorliq formulasi](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md)da saqlangan. V2 hisobotdagi v3 test: precision `.1009`, recall `.3548`, PR-AUC `.1134`, ROC AUC `.7714`. O‘sha modelning aniq commit kodi va to‘liq logi joriy Git tarixida **qayd etilmagan**. Kambag‘al precision — ko‘p yolg‘on signal; “yaxshilash” uchun testni bezash emas, simulyatsiya taxminlarini ochish kerakligi ma’lum bo‘ldi. V3 va v4 o‘rtasida generator ham almashgan; demak raqamlar algoritmning nazoratli yutug‘i emas.

## 4-bob. v3 → v4: ssenariylar va vaqt oqimi

`fraud_detector/event_stream.py` to‘rtta firibgarlikka o‘xshash tipologiya (`account_takeover`, `card_testing`, `mule_cashout`, `new_account_transfer`), qonuniy sayohat va katta xarid, normal voqealarni yaratadi. `velocity_1h` va `prior_declines_24h` joriy qator **tarixga qo‘shilishidan oldin** deque oynasidan olinadi. `tests/test_upgrade.py::test_scenarios_and_past_only_rolling_windows` har bir qator uchun qayta hisoblaydi. Ssenariy/ID/label modelga berilmaydi. Bu qator darajasidagi future leakage’ni cheklaydi, lekin generatorning o‘zi yorliqni xususiyatlar bilan bog‘laydi — tashqi haqiqiylik yo‘q.

## 5-bob. Vaqt bo‘yicha baholash va baseline

`fraud_detector/training_v2.py`da v4 fit 7800, calibration 1200, validation 3000, keyingi mustaqil test 3000 bo‘lgan; model C va chegara validatsiyada tanlangan. `fraud_detector/evaluation.py` always-normal, qoida va logistika modelini hisoblaydi. V4 test: TP167 FP69 FN9 TN2755, precision `.707627`, recall `.948864`, PR-AUC `.893556` ([aniq jadval](MODEL_EVALUATION.md)). Biroq `docs/MODEL_EVALUATION.md`ning tarixiy jadvalida nominal 5% ML chegarasi 232/3000 = **7.733%** alert bergan; u teng hajmli solishtirish emas edi. V5 exact top-k’ni asosiy ko‘rinishga o‘tkazdi, 0.5/1/5/10% hajmni aniq ushlaydi; validation chegaralari alohida va haqiqiy alert foizi bilan qoladi.

## 6-bob. Analitikning qo‘li, tizimning chegarasi

`fraud_detector/api_v2.py` bir tranzaksiyani ballaydi, qat’iy CSV batch’ni qabul qiladi, SQLite’da `new → in_review → confirmed_fraud/false_positive` holatini, izohni va auditni saqlaydi. `fraud_detector/reporting.py` JSON/HTML/PDF/CSV eksport beradi. Modelning `coefficient × standardized value` hissasi hisobni izohlaydi; API’dagi qo‘lda yozilgan signallar boshqa narsa. Ular sababiy isbot emas. Hech bir kod karta/to‘lovni bloklamaydi. `tests/test_upgrade.py` status, note-only audit, eksport va noto‘g‘ri kirishni tekshiradi.

## 7-bob. Xatolar daftarining birinchi qismi — v4 gacha qayd etilganlar

Har qatorda kuzatilgan holat → joy/dalil → sabab → tuzatish/natija berilgan. Aniq ilk commit yo‘q bo‘lsa **qayd etilmagan** deb yozamiz.

| Kuzatuv | Qayerda va dalil | Sabab, tuzatish, natija |
|---|---|---|
| Kichik calibration bo‘lagida model yiqilgan | `training_v2.py`, v2 hisobot: calibrationda faqat bitta class | `LogisticRegression` ikki class talab qiladi. `IdentityCalibrator` fallback qo‘shilgan; testlar o‘tgan. Dastlabki stack trace **qayd etilmagan**. |
| Ruff `unnecessary int cast` e’tirozi | v2 hisobot, Ruff tekshiruvi | Keraksiz cast olib tashlangan; keyingi Ruff `All checks passed`. Faylning avvalgi satri **qayd etilmagan**. |
| CSV body to‘liq xotiraga o‘qilgan | `api_v2.py::batch_score`, v2 hisobot | Streaming 1 MB limit va 1000-qator cap qo‘shilgan; oversized test 413. |
| Note-only o‘zgarish mumkin emas edi | `api_v2.py::update_review`, v2 hisobot | Bir xil status + boshqa note uchun `note_change` audit qo‘shilgan; API/Chrome test o‘tgan. |
| PDF uzun UZ/RU so‘zni kesishi mumkin edi | `reporting.py`, v2 hisobotdagi `pdftotext` sinovi | Glyph-eni bo‘yicha wrap/sahifa davom ettirish; 18/18 UZ va 18/18 RU qayta o‘qilgan. |
| CSV formula va sust validatsiya | `api_v2.py`, `reporting.py`, v2 hisobot/testlar | CSV boolean `true/false`, qo‘shimcha JSON maydonlari rad, bo‘shliqdan keyingi formula quote qilingan; regression testlar o‘tgan. |
| Eski pip auditida advisorylar | v2 hisobot: pip 24.0 uchun 12 advisory | Izolyatsiyalangan `.venv` pip 26.2.1 ga yangilangan; o‘sha paytdagi `pip-audit` “No known vulnerabilities found”. Bu sertifikat emas. |
| Patch `.orig/.rej` qoldiqlari | v2 hisobotdagi aniq 11 fayl ro‘yxati | Faqat ish jarayoni nusxalari olib tashlangan; foydalanuvchi ma’lumoti o‘chirilmagan. |

## 8-bob. CI va ochiq v2.0.0 release

Git tarixi: `4da0fb3` dastlabki release commit, `07b05da` CI va hisobot yangilanishi, `0babd0d` tekshirilgan CI havolasi. [GitHub Actions run 38786481512](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/38786481512) success; `v2.0.0` [release](https://github.com/shomatoff/ai-bank-fraud-detector/releases/tag/v2.0.0) chiqarilgan. `actions/checkout`/`setup-python` eski Node ogohlantirishlari `@v7`, Ubuntu 24.04 bilan almashtirilgan; yakuniy v2 CI muvaffaqiyatli. Bu v5 kodini GitHub’da bor degani **emas**: v5 mahalliy, push/release uchun yangi ruxsat olinmagan.

## 9-bob. v5 audit: qiyinroq vazifa, pastroq raqam

`event_stream.py`da yangi `legit_many_declines` qo‘shildi, fraud ssenariy yorlig‘i `.94→.88`, normal `.005→.01`. Fit/calibration/validation 60/20/20 bo‘ldi. Birinchi v5 hisob eski test seed 200045’dan foydalangani sezildi — `training_v2.py` va `scripts/v5_evaluation.py` test seed’ni **300045** va 300045–300054 oilasiga almashtirdi, natijalar qayta ishlandi. Dastlabki qayta ishlatilgan seed natijasi precision `.640816`, recall `.844086`, PR-AUC `.713471` edi; **final v5 emas**. Final yangi testda TP164 FP90 FN25 TN2721, precision `.645669`, recall `.867725`, PR-AUC `.796689`. Bu ham v2’dan past; generator, split va test seed birga o‘zgargani uchun sababni bittaga yuklab bo‘lmaydi.

10 to‘liq pipeline seed’i uchun exact-5% precision o‘rtacha `.813333` (95% seed-bootstrap [.800667,.828667]), recall `.661446` ([.648752,.674807]), PR-AUC `.731488` ([.715733,.750300]); `scripts/v5_evaluation.py` va `data/v5_evaluation.json` (Git’da emas). Tipologiya chiqarib tashlanganda `card_testing` testida TP0/FN41. Card-present default chegarada TP0/FN14, lekin 14 musbat qator yetarli emas: UI `not evaluable (<30 positives)` ko‘rsatadi.

## 10-bob. v5 xatolar daftarining ikkinchi qismi

| Kuzatuv | Qayerda va dalil | Sabab, tuzatish, natija |
|---|---|---|
| Avvalgi test CSRF bilan 201 kutdi, 401 oldi | `tests/test_foundations.py::test_report_migration_details_and_json_export`, pytest: 1 failed / 15 passed | Yangi `X-API-Key` majburiy. Test key bilan yangilandi; oxirgi test natijasi [v5 hisobotda](../IMPLEMENTATION_REPORT_UZ.md#qoshimcha-hisobot-v5). |
| Ruff import tartibi va `BLE001` | `fraud_detector/api_v2.py`, `public_benchmark.py`, `tests/test_public_benchmark.py`; Ruff chiqishi | Importlar tartiblandi, umumiy `Exception` o‘rniga ma’lum optional-explainer xatolari tutildi; Ruff qayta o‘tdi. |
| Kattaroq Platt ham validationni yomonlashtirdi | `training_v2.py`, validation Brier `.017899→.018520`, ECE `.014630→.018282` | “Kalibrlash har doim yaxshi” taxmini noto‘g‘ri. Ikkisi yaxshilanmasa identity ishlaydi; final model raw logistic. |
| HMACsiz hash oson qayta yozilishi mumkin | `api_v2.py` oldingi faqat SHA256; `tests/test_upgrade.py::test_artifact_hmac_rejects_rewritten_hashes` | Lokal 0600 kalit bilan SHA256 juftligi HMAC qilindi va `joblib.load`dan oldin tekshirildi. Kalit ham shu katalogda: bank-grade emas. |
| ULB manba URL sinovi HTTP 404 | `curl -I -L` on `https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud` | Kalitsiz endpoint bu muhitda mavjud emas; yuklashga aylanma yo‘l/credential ishlatilmadi. Loader sintetik fixture bilan sinaldi; real ULB natijasi **yo‘q**. |
| XGBoost install 305 MB CUDA dependency so‘radi | `.venv/bin/python -m pip install xgboost shap` chiqishi | Ortiqcha yuklash bekor qilindi; `lightgbm==4.7.0`, `shap==0.53.0` o‘rnatildi. XGBoost natijasi **yo‘q**. |
| SHAP LightGBM ogohlantirishi | pytest: 18 passed, 1 warning; `shap/explainers/_tree.py:579` | Upstream output list/array farqi; `public_benchmark.py::_explanation` ikkisini normalizatsiya qiladi. Ogohlantirish qolgan, natija yashirilmagan. |
| Feedback demo yomonlashdi | 300 qatorli **sintetik fixture**, `data/fixture_benchmark_results.json` | Idealized 30 validation label bilan qayta o‘qitish: test PR-AUC `.152906→.124331`, exact-5% TP `1→0`; real analitik feedback emas. |
| Docker build bajarilmadi | `docker build -t sentinelai-v5-local .`: exit 127 | `docker` o‘rnatilmagan; build/run/health containerda **qayd etilmagan**. Lokal venv API health 200. |

## 11-bob. Nimani noto‘g‘ri tushundik?

Yakuniy lokal qayta tekshiruv (2026-10-16): `pytest -q` — **21 passed, 1 LightGBM/SHAP warning**; `ruff check fraud_detector tests scripts` — **All checks passed**; `pip-audit` — **No known vulnerabilities found**; `pip check` — **No broken requirements found**. `scripts/live_smoke.py`da 19 HTTP tekshiruvning kutilgan 200/201/401/403/422 statuslari o‘tdi; Chrome 9 ta haqiqiy screenshot oldi. 24 Markdown faylda 0 singan lokal havola. Bu natijalar Docker va real public benchmark o‘rnini bosmaydi.

“Nominal 5%” haqiqiy 5% emas: v2 ML 7.733%, v5 8.4% testni belgiladi. Sintetik yorliqlar oson ssenariy naqshlari tufayli natijani oshirishi mumkin. Platt v4 test Brier’ni `.012016→.012800` yomonlashtirgan, v5 validationda ham foyda bermagan. Card-present v4 TP0/FN4, v5 TP0/FN14; kichik kesmada recallni ishonchli baholab bo‘lmaydi. “Yuqori aggregate recall yangi firibgarlikni topadi” xulosasi noto‘g‘ri: held-out card testing TP0/FN41. `joblib` HMAC bilan ham noto‘g‘ri manbadan yuklanmasligi kerak. Public ULB fixture metrikasi ULB metrikasi emas.

## 12-bob. Bu loyiha nima, nima emas?

Bu — uch tilli FastAPI+HTML/JS, faqat sintetik ilova; testli ssenariy generatori, logistika, baseline, lokal analitik jarayoni, hisobot eksporti, cheklovlari ochiq tadqiqot portfeli. [Benchmark loader](BENCHMARK.md) alohida va ixtiyoriy. Bu — bank-grade xavfsizlik, haqiqiy bankga integratsiya, mijoz firibgarligini isbotlash, zaiflik skaneri, avtomatik bloklovchi yoki production deployment emas. Docker runtime, real public benchmark, shadow evaluation, bias/fairness audit, real feedback, kalitlarni boshqarish va mustaqil xavfsizlik tekshiruvi **bajarilmagan**. Yangi ish uchun birinchi qoida: yangi data manbasi, huquqiy asos, maxfiylik va inson nazoratisiz modelni bank qaroriga ulamaslik.
