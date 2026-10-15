# SentinelAI — yakuniy to‘liq ish hisoboti (v4)

Sana: 2026-10-15. Holat: ishlaydigan, faqat sintetik ma’lumotli FastAPI + HTML/JavaScript portfolio ilovasi. Haqiqiy bank, mijoz, credential, to‘lov API yoki karta bloklash ishlatilmagan. Master prompt fayli workspace/Desktop qidiruvida topilmadi; shu sabab uning 100% bajarilgani da’vo qilinmaydi. Kod ochiq [GitHub repository](https://github.com/shomatoff/ai-bank-fraud-detector) `main` branchiga yuborilgan. [GitHub Actions CI](https://github.com/shomatoff/ai-bank-fraud-detector/actions) tekshirilgan; [v2.0.0 release](https://github.com/shomatoff/ai-bank-fraud-detector/releases/tag/v2.0.0) source ZIP/tarball orqali yuklab olinadi. LinkedIn/Telegram matnlari draft, post qilinmagan.

## Nimalar qo‘shildi va yangilandi

- Ssenariyli event generator: account takeover, card testing, mule/cash-out, new-account transfer; legitimate travel/large purchase edge cases; normal shovqin. Yorliq v4 `is_fraud = 1{U < p_s}`: fraud ssenariylar .94, qonuniy edge .01, normal .005. Eski v3 sigmoid yorliq formulasi retired.
- Customer-level chronological stream: `velocity_1h` va `prior_declines_24h` faqat oldingi voqealardan rolling deque bilan hisoblanadi; joriy/kelajak voqea va label kirmaydi. Metadata modelga kiritilmaydi.
- Vaqt bo‘yicha fit 7,800 / calibration 1,200 / validation 3,000; yangi seed 200045 bilan untouched test 3,000. Candidate va threshold faqat validationda tanlandi. Logistic regression C=1.0 tanlandi; disjoint Platt calibration mavjud.
- Always-normal, frozen rule baseline va ML baseline bir xil nominal 5%/10% alert budgetlarda; retrospective exact top-k alohida belgilangan. PR/ROC/reliability curves, editable FP/FN cost threshold preview, PSI drift simulation va channel/country-risk/account-age slices.
- Modelga asoslangan exact linear log-odds contribution va alohida descriptive rules; ular causal explanation emas. Analyst workflow: `new → in_review → confirmed_fraud/false_positive`, notes, SQLite audit, CSV/JSON/HTML/PDF export. Batch CSV: exact header, UTF-8, 1 MB/1000-row limit, streaming size cap.
- Artifact SHA256 integrity check, model/data cards, Dockerfile (local only), Makefile, EN/UZ/RU docs, authentic Chrome screenshots, updated CI, dependency versiyalarining `constraints-verified.txt` fayli, lokal integratsiya qo‘llanmasi va release draftlari.

## Haqiqiy bajarilgan natijalar

`.venv/bin/python -m fraud_detector.model` yakuniy testida: prevalence 176/3000 = 5.8667%; threshold .08581994158148241; TN2755 FP69 FN9 TP167; precision .707627; recall .948864; F1 .810680; PR-AUC .893556; ROC AUC .977438; FPR .024433; calibrated Brier .012800, raw Brier .012016. Kalibrlash bu testda yaxshilanmadi. Card-present slice recall 0/4. Bu sintetik generatorni o‘rganish natijasi, real bank samaradorligi emas.

Always-normal: 0 alert, TP0 FP0 FN176 TN2824, PR-AUC .058667, ROC .5. Fixed rule: PR-AUC .750108, ROC .970813; validation-derived 5% test TP147/FP72/FN29/TN2752, precision .671233, recall .835227; 10% TP165/FP207/FN11/TN2617, precision .443548. ML: nominal 5% TP167/FP65/FN9/TN2759, precision .719828, recall .948864; nominal 10% TP169/FP184/FN7/TN2640, precision .478754, recall .960227. Exact same-volume retrospective ML top-k: 5% precision .92/recall .784091; 10% precision .563333/recall .960227. Exact tables [MODEL_EVALUATION](docs/MODEL_EVALUATION.md)da.

V3 old test: precision .1009, recall .3548, PR-AUC .1134, ROC .7714. V4 bilan taqqoslash controlled algorithm improvement emas — generator, labels va split dizayni o‘zgargan.

## Test va tekshiruvlar

- `pytest -q`: **16 passed** (joriy auditdan keyin). `-W error::DeprecationWarning` rejimida ham **16 passed**.
- `ruff check fraud_detector tests scripts`: **All checks passed**.
- `.venv/bin/pip-audit -r requirements.txt`: runtime requirementlarda **No known vulnerabilities found**. Dastlab butun `.venv` auditi eski `pip 24.0` uchun 12 advisory qaytardi; `pip 26.2.1` ga ko‘tarilgach `.venv/bin/pip-audit` **No known vulnerabilities found** qaytardi. Bu vaqtga bog‘liq skan natijasi, xavfsizlik sertifikati emas.
- Live API on 127.0.0.1:8002: health/config/metrics/overview/transactions/docs 200; score 200; threshold preview 200; valid batch 200; malformed batch 422; CSRF 403; report create 201; review/audit/JSON/HTML/PDF/CSV exports 200.
- Real Chrome/CDP capture: **8 ta** haqiqiy screenshot; overview, scoring, model izohi, status va note-only audit, curves, PSI/slices, uch til DOM tekshiruvlaridan o‘tdi. Fayllar: [screenshots](screenshots/README.md).
- Model artifact/API consistency va hash rejection testlari o‘tdi. `TestClient/httpx` deprecation rejimi ham xatosiz o‘tdi (`httpx 0.28.1`, Starlette 1.8.0). Barcha 20 Markdown hujjatidagi lokal havolalar tekshirildi: **0 ta singan havola**. `node --check web/app.js` o‘tdi. Public GitHub-hosted [dastlabki CI](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/38786055291) va [release commit CI](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/38786481512) **success**: Ruff, pytest, pip-audit, model training va metrics assertion o‘tdi. Ikkinchi run `07b05da` commitiga tegishli va Actions v7, Ubuntu 24.04 bilan bajarilgan. Docker runtime bajarilmadi.

## Ishlatilgan texnologiyalar va xatolar

Python 3.12.3, FastAPI, Uvicorn, Pydantic, NumPy, pandas, scikit-learn, joblib, SciPy, SQLite, reportlab, pytest, Ruff, httpx 0.28, pip-audit, Node.js/Chrome CDP, HTML/CSS/JavaScript, Make/YAML. Dastlab kichik testda calibration slice faqat 0 class bo‘lib LogisticRegression yiqildi; `IdentityCalibrator` fallback qo‘shildi va testlar o‘tdi. Ruff unnecessary int cast xatosi tuzatildi. CSV body oldin to‘liq o‘qilardi; streaming 1 MB cap qo‘shildi. Eski hujjatlardagi v3 generator/gradient boosting/0.07252654 ma’lumotlari v4 bilan almashtirildi. Sandbox patch xatolari bo‘lganda faqat aniq fayl yo‘llari bilan qayta tekshirildi; sudo ishlatilmadi.

Joriy auditdagi qo‘shimcha topilmalar va yechimlar:

| Topilma | Aniq yechim va dalil |
|---|---|
| Statusni o‘zgartirmasdan izohni tahrirlab bo‘lmasdi | `PATCH` note-only update va `note_change` audit yozuvi qo‘shildi; API va Chrome orqali tasdiqlandi. |
| PDF uzun uzluksiz yoki UZ/RU matnni kesishi mumkin edi | Glyph eni bo‘yicha satrlarga bo‘lish va sahifa davom ettirish qo‘shildi; `pdftotext` 18/18 UZ va 18/18 RU namunani qayta o‘qidi. |
| CSV boolean va qo‘shimcha JSON maydonlari sust qabul qilinardi | CSV boolean faqat `true/false`; Report/Review/Threshold uchun `extra=forbid`; regression testlar qo‘shildi. |
| CSV eksportida bo‘shliqdan keyin formula boshlanishi ehtimoli | Izoh boshidagi bo‘shliqdan keyingi `= + - @` belgilari ham quote bilan himoyalandi; test o‘tdi. |
| Dashboarddagi eski split/versiya, qisman tarjima | Metodologiya 65/10/25 ga tuzatildi, footer v2.0, model izohlari va slice nomlari uch tilda chiqarildi; yangi Chrome capture o‘tdi. |
| Keng dependency diapazonlari metrikani takrorlashni qiyinlashtirardi | Tekshirilgan asosiy versiyalar `constraints-verified.txt` ga yozildi; install dry-run muvaffaqiyatli. |
| Eski pip versiyasida advisorylar bor edi | `.venv` pip 24.0 → 26.2.1; installed-environment audit qayta bajarildi va 0 known vulnerability chiqdi. |
| Demo hujjatida server 8000, curl esa 8001 edi | Barcha demo HTTP komandalar 8000 ga moslandi. |
| Patch utilitasi `.orig/.rej` qoldirgan edi | Faqat shu ishga tegishli patch qoldiqlari olib tashlandi; foydalanuvchi ma’lumoti o‘chirilmadi. |

### Fayllar bo‘yicha aniq o‘zgarishlar

- Yangi hujjatlar: `docs/LOCAL_INTEGRATION.md`, `docs/FRAUD_DETECTION_CAPABILITIES.md`, `docs/MODEL_EVALUATION.md`, `docs/BANKING_INTEGRATION_ROADMAP.md`, uch tildagi sintetik yorliq formulasi va qo‘llanmalar, model/data cards, ushbu hisobot, release/social post draftlari. `constraints-verified.txt`, `Dockerfile`, `Makefile`, CI workflow va haqiqiy screenshotlar qo‘shildi.
- Yangilangan kod: `fraud_detector/synthetic.py` (ssenariy va tarix), `fraud_detector/model.py` (vaqt bo‘yicha baholash, baseline, calibration, explanation, drift), `fraud_detector/api.py` (scoring, strict batch, analyst workflow, eksport, xavfsiz validatsiya), `fraud_detector/reporting.py` (HTML/PDF/CSV), `web/index.html`, `web/app.js`, `web/styles.css` (uch til va diagnostika), `tests/` va `scripts/`. Aniq interfeys va metrikalar yuqorida hamda bog‘langan docs’da.
- Olib tashlanganlar: patchdan qolgan `.github/workflows/ci.yml.orig`, `fraud_detector/evaluation.py.orig`, `web/app.js.orig`, `web/index.html.orig`, `.gitignore.orig`, `requirements-dev.txt.orig`, `requirements.txt.orig`, `tests/test_app.py.orig`, `tests/test_app.py.rej`, `tests/test_foundations.py.orig`, `tests/test_foundations.py.rej`. Bular ish jarayonida hosil bo‘lgan vaqtinchalik nusxalar edi; real data yoki foydalanuvchi hujjati o‘chirilmagan. `.gitignore` kelajakdagi `.orig/.rej`, cache, `.venv`, model artifact va SQLite fayllarini Git’dan chetlatadi.
- Aylanib o‘tilmagan cheklovlar: Docker runtime bu muhitda tekshirilmagan; haqiqiy bank bilan test, security pentest, production deployment va master prompt bo‘yicha gap analysis amalga oshirilmagan. Ularni “bajarildi” deb belgilamaymiz.

## Hali NOT IMPLEMENTED / risklar

Real bank integration, read-only shadow production evaluation, authentication/RBAC, signed artifacts, tamper-evident centralized audit, live drift alerts, fairness/bias study, chargeback/delayed labels, real currency/geography/device intelligence, case assignment/SLA, vulnerability scanning, Streamlit, automatic payment/card blocking va bank-grade security yo‘q. `joblib` hash integrity, signature emas. Synthetic high metrics production readiness bermaydi; false positive/negative va subgroup failure mavjud.

## Linux launch

```bash
cd /home/chainjas/codex-test/ai-bank-fraud-detector
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m scripts.generate_data --rows 12000 --seed 42
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m pytest -q
.venv/bin/ruff check fraud_detector tests scripts
.venv/bin/pip-audit
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Brauzerda server ishlayotgan paytda `http://127.0.0.1:8000/` ni oching; port band bo‘lsa 8001 ni ikkala joyda ham almashtiring. Docker local lab komandasi README’da. To‘liq capability/formula/roadmap: [audit](docs/FRAUD_DETECTION_CAPABILITIES.md), [formula UZ](docs/SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md), [roadmap](docs/BANKING_INTEGRATION_ROADMAP.md), [demo](docs/DEMO_WALKTHROUGH.md).

GitHub’dan mustaqil yuklash uchun yuqoridagi `cd` qatoridan oldin `git clone https://github.com/shomatoff/ai-bank-fraud-detector.git` va `cd ai-bank-fraud-detector` ishlating; ya’ni mashinangizda loyiha mavjud bo‘lmasa `/home/chainjas/...` yo‘li sizda bo‘lmaydi. `git clone` o‘rniga GitHub release source ZIP ham ishlaydi. Lokal integratsiya HTTP API misollari [LOCAL_INTEGRATION](docs/LOCAL_INTEGRATION.md)da.
