# SentinelAI — yakuniy to‘liq ish hisoboti (v4)

> 2026-10-18 yangilanishi: ushbu matnning v4/v5 raqamlari tarixiy. Joriy v6-local baholash [MODEL_EVALUATION](docs/MODEL_EVALUATION.md)da. **Modelni qanday ma’lumotga o‘qitish bo‘yicha manbali, ustuvor va bosqichli tavsiyalar** hamda bajarilgan 1-bosqich auditi [AI_TRAINING_ROADMAP_UZ](docs/AI_TRAINING_ROADMAP_UZ.md)da. Avvalgi “master prompt topilmadi” gapi tarixiy: fayl endi loyiha papkasida mavjud va [gap analysis](docs/MASTER_PROMPT_GAP_ANALYSIS.md) yozilgan.

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

## Qo'shimcha hisobot v5

Sana: 2026-10-15–16. **Bu bo‘lim avvalgi v2.0.0 hisobotiga faqat ilova qilingan; yuqoridagi matn tarixiy holat sifatida o‘zgartirilmagan.** V5 kod va hujjatlar hozir faqat lokal workspace’da. Foydalanuvchining ushbu topshirig‘iga binoan GitHub’ga push, release yoki ijtimoiy tarmoqqa post qilinmadi; GitHub’dagi `v2.0.0` hali eski chiqarilgan versiya.

### Bosqich A — rigor va lokal xavfsizlik

- `fraud_detector/evaluation.py`: exact top-k 0.5%, 1%, 5%, 10% endi qoida/ML solishtirishining asosiy usuli; nominal validation cutoff natijalarida haqiqiy test alert foizi alohida. Always-normal 0 alert bo‘lib qoladi, budgetni sun’iy to‘ldirmaydi. Retrospektiv top-k to‘liq batch scoringni talab qiladi va jonli threshold emas.
- `fraud_detector/event_stream.py`: qonuniy `legit_many_declines` (2.5%, epizod 5, rad etish .85, yorliq .02) qo‘shildi; to‘rtta fraud ssenariyining ijobiy yorliq ehtimoli `.94→.88`, normal `.005→.01`. Haqiqiy bank statistikasi emas. Card-present hajmi metrikani bezash uchun sun’iy oshirilmadi; 30 tadan kam ijobiy satrda recall “not evaluable” bo‘ladi.
- `fraud_detector/training_v2.py`: 60/20/20 vaqt split, yangi test seed **300045**, 10 seed to‘liq qayta o‘qitish; Platt faqat validation Brier va 10-bin ECE **ikkalasi** yaxshilansa qo‘llanadi. Raw Brier `.017899`, Platt `.018520`; raw ECE `.014630`, Platt `.018282` — shuning uchun v5 Platt o‘chirilgan. Model izohi tanlangan model log-oddsiga aniq chiziqli hissa, sababiy emas.
- `fraud_detector/api_v2.py`: hisobot yaratish/yangilashga lokal analyst/admin `X-API-Key` **va** CSRF kerak; `confirmed_fraud` faqat admin. Kalitlar `data/local-api-keys.json`da 0600 ruxsat bilan yaratiladi yoki ikki alohida environment kaliti ishlatiladi. Model va validation SHA256 juftligi lokal 0600 kalit bilan HMAC qilinib `joblib.load`dan oldin tekshiriladi. Kalit artefakt yonida saqlanadi, read/export autentifikatsiyasiz: bu bank-grade himoya emas. Hech qanday avtomatik bloklash qo‘shilmadi.
- Docker: `docker build -t sentinelai-v5-local .` haqiqatan sinab ko‘rildi, `/bin/bash: docker: command not found` (exit 127). Shuning uchun Docker build/run va konteyner `/api/health` **bajarilmadi**; oddiy venv live `/api/health` 200 qaytdi.

### Bosqich B — public benchmark chegarasi

`fraud_detector/public_benchmark.py` ULB sxemasidagi `Time,V1..V28,Amount,Class` CSV’ni faqat foydalanuvchi bergan SHA256 mos bo‘lsa ochadi, `Time` bo‘yicha 60/20/20 ajratadi. Logistic, histogram gradient boosting, o‘rnatilsa LightGBM/XGBoost, amount-only qoida va always-normal taqqoslanadi. Tree SHAP va logistika linear hissalari sababiy emas. Idealized analyst feedback faqat validationning oldingi yarmidagi sun’iy “tasdiqlar” bilan ko‘rsatiladi. Dataset appga ulanmagan va repoga kiritilmagan. Kalitsiz Kaggle yuklash urinishida HTTP 404 qaytdi; **haqiqiy ULB CSV olinmadi, unda model ishlatilmadi, public-data metrikasi yo‘q**. `docs/BENCHMARK.md` aniq qo‘llanma va cheklovni beradi.

300 satrli **sintetik ULB-sxema fixture** (test 60, ijobiy 7) smoke natijasi: validation HGB’ni tanladi; test PR-AUC logistic `.134998`, HGB `.152906`, LightGBM `.140056`, amount-only qoida `.186839`. Exact-5% uch alertda HGB precision `.333333`, recall `.142857`; logistic/LightGBM/rule precision va recall 0. Idealized feedback HGB test PR-AUC’ni `.152906→.124331` va TP’ni `1→0` yomonlashtirdi. Bular haqiqiy ULB natijalari **emas**. XGBoost install 305 MB CUDA dependency so‘radi va bekor qilindi; LightGBM 4.7.0/SHAP .53 o‘rnatildi. SHAP’ning LightGBM chiqish-shakli haqida 1 upstream warning qoldi, natija normallashtirildi.

### Oldin/keyin — faqat o‘lchangan sintetik testlar

| Ko‘rsatkich | v2.0.0/v4, eski generator va seed 200045 | v5-local, o‘zgargan generator va **yangi** seed 300045 |
|---|---:|---:|
| Test qatorlari / fraud yorliqlari | 3000 / 176 | 3000 / 189 |
| Fit / calibration / validation | 7800 / 1200 / 3000 | 7200 / 2400 / 2400 |
| Default cutoff alerts | 236 (7.8667%) | 254 (8.4667%) |
| TP / FP / FN / TN | 167 / 69 / 9 / 2755 | 164 / 90 / 25 / 2721 |
| Precision | .707627 | .645669 |
| Recall | .948864 | .867725 |
| F1 | .810680 | .740406 |
| PR-AUC | .893556 | .796689 |
| ROC AUC | .977438 | .934317 |
| Test Brier (tanlangan model) | .012800, Platt | .021669, raw logistic |

Bu jadval **nazoratli algoritm A/B sinovi emas**: generator, yorliq shovqini, split va test seed birga o‘zgargan. V5 exact-5% *teng hajm* testida rule TP91/FP59/FN98/TN2752, precision `.606667`, recall `.481481`; ML TP130/FP20/FN59/TN2791, precision `.866667`, recall `.687831` — ikkisida ham aynan 150/3000 (5%) alert. Nominal 5% cutoff esa ML’da 252/3000 (8.4%) alert; endi bu farq yashirilmaydi. 10 mustaqil seed (42–51, yangi test seedlari 300045–300054), exact-5% mean va 95% seed-level bootstrap: precision `.813333` [.800667,.828667], recall `.661446` [.648752,.674807], PR-AUC `.731488` [.715733,.750300]. Bu interval faqat simulyator o‘zgaruvchanligi uchun. Held-out `card_testing`: **TP0/FN41**; card-present default TP0/FN14, recall 30 tadan kam positive sabab “not evaluable”. To‘liq jadval: `docs/MODEL_EVALUATION.md`.

### Bajarilgan tekshiruvlar, xatolar va qolgan ish

`.venv/bin/python -m pytest -q`: **21 passed, 1 warning** (LightGBM SHAP output-shape). `.venv/bin/ruff check fraud_detector tests scripts`: **All checks passed**. `.venv/bin/pip-audit`: **No known vulnerabilities found** (faqat joriy vaqt). `node --check` ikkala JS faylda o‘tdi. Live `scripts/live_smoke.py --base http://127.0.0.1:8003`: `/`, `/docs`, health, metrics, overview, transactions, score, reports va eksport 200; noto‘g‘ri CSV 422; kalitsiz write 401; analyst create 201; analyst `confirmed_fraud` 403; admin confirmation 200. Chrome/CDP uch til va analyst auditini tekshirib **9 ta haqiqiy screenshot**ni `screenshots/`ga oldi. Docker sinovi yuqorida keltirilgan 127 xato bilan tugadi.

Rivojlanishda uchragan aniq xatolar: yangi API-key sabab eski `test_report_migration_details_and_json_export` 401 olib, dastlab `1 failed / 15 passed` bo‘ldi — test yangi auth siyosatiga moslandi; Ruff import tartibi va keng exception tutishni ko‘rsatdi — tartiblandi; birinchi v5 hisob eski 200045 test seed’ni qayta ishlatgani sezildi — 300045 ga ko‘chirilib 10 seed bilan qayta hisoblandi; Platt validationni yomonlashtirdi — shartli o‘chirildi; Kaggle URL 404; Docker yo‘q; XGBoost CUDA download bekor qilindi. Sabab/joy/dalil/tuzatish to‘liq ikki tildagi hujjatli hikoyada: `docs/PROJECT_DOCUMENTARY_UZ.md`, `docs/PROJECT_DOCUMENTARY_EN.md`.

**NOT IMPLEMENTED / NOT RUN:** haqiqiy ULB benchmark, XGBoost natijasi, Docker runtime, production key management/RBAC, report read-auth, imzolangan tashqi trust root, real analyst feedback, bank/shadow integration, fairness audit, pentest, avtomatik bloklash. Master prompt `AI_BANK_FRAUD_DETECTOR_CODEX_MASTER_PROMPT.md` project papkasida topilmadi; requirement-by-requirement gap analysis qilib bo‘lmaydi. V5 GitHub’da **yo‘q**, release/post **qilinmadi**.

### V5 lokal ishga tushirish

```bash
cd /home/chainjas/codex-test/ai-bank-fraud-detector
python3 -m venv .venv
.venv/bin/python -m pip install -c constraints-verified.txt --upgrade pip
.venv/bin/python -m pip install -c constraints-verified.txt -r requirements-dev.txt
.venv/bin/python -m fraud_detector.model
.venv/bin/python -m pytest -q
.venv/bin/ruff check fraud_detector tests scripts
.venv/bin/pip-audit
.venv/bin/uvicorn fraud_detector.api:app --host 127.0.0.1 --port 8000
```

Brauzerda **server ishlayotgan paytda** `http://127.0.0.1:8000/` ochiladi. Hisobot yozishdan oldin o‘z kompyuteringizdagi `data/local-api-keys.json`dan analyst kalitini UI’dagi password maydoniga kiriting; admin tasdiqlash uchun admin kaliti kerak. Kalitni hech kimga yubormang. Alohida terminalda `.venv/bin/python -m scripts.live_smoke --base http://127.0.0.1:8000` orqali live API’ni tekshirish mumkin. Public benchmark qo‘shimcha deps va qat’iy checksum qadamlari `docs/BENCHMARK.md`da. Docker buyruqlari faqat Docker mavjud muhitda sinab ko‘rilishi mumkin.

## 2026-10-18 qo‘shimcha hisobot — AI yaxshilash tajribasi va xavfsiz qaror

Eski v4/v5 tarixiy matn o‘zgartirilmadi; bu bo‘lim joriy holatni qo‘shadi. To‘liq protokol, raqamlar, xatolar va qolgan bosqichlar [AI_CHALLENGER_EVALUATION_UZ](docs/AI_CHALLENGER_EVALUATION_UZ.md) hamda [AI_TRAINING_ROADMAP_UZ](docs/AI_TRAINING_ROADMAP_UZ.md)da.

- Mavjud 10 belgi asosida 4 ta past/joriy voqeagagina tayanadigan interaction yaratildi; yorliq, ssenariy va customer ID kiritilmadi. Nomzod alohida qoldi, faol v6 modelga qo‘shilmadi.
- Mustaqil 10-seed tasdiqda validation-selected yangi siyosat exact-5% precision 0,8360 → 0,8653, recall 0,6703 → 0,6938, PR-AUC 0,7566 → 0,7680 ko‘rsatdi. Lekin boshqa, 342-seed held-out typology gate uch turda recall regressiyasini aniqladi: account takeover 0,4887 → 0; mule/cash-out 0,9165 → 0,1671; new-account transfer 0,55 → 0. Card testing ikkala modelda ham 0. **Promotion rad etildi**, `promote=false`; ijobiy umumiy metrika bu xavfni yashirmaydi.
- Oldin ko‘rilgan 42–51 test seedlariga v7 sinov ham o‘tkazildi, ammo bu mustaqil final tasdiq emas. Birinchi holdout tekshiruvining model-selection qoidasi deployment qoidasi bilan mos emasligi aniqlandi va tuzatilgan mos diagnostikada ham regressiya saqlandi. Dastlab v6 zaxira deb nomlangan fayl test importidagi avtomatik trening sabab aslida v7 preflight ekani aniqlanib qayta nomlandi; asl v6 backup deb ko‘rsatilmaydi.
- Rasmiy ULB CSV download 404 qaytardi, hisob ma’lumoti/CSV yo‘q; real benchmark bajarilmadi. Uchinchi tomon nusxasidan foydalanilmadi. Keyingi bosqich: asl fayl/checksum va foydalanish shartlari, keyin alohida benchmark va yangi mustaqil final test; real bank/shadow validation hali yo‘q.
- GitHub’dagi `shomatoff/ai-bank-fraud-detector` repo `PRIVATE`ga o‘tkazildi va GitHub `isPrivate=true` deb tasdiqladi. Bu oldingi public nusxalarni o‘chirib yubormaydi. `data/`dagi model, natija, API-key va SQLite Git’ga qo‘shilmaydi. Joriy pytest **29 passed, 1 SHAP warning**; Ruff **clean**. Git push/CI natijasi quyida alohida qayd etiladi.

### Qo‘shimcha Git va gate natijasi

`d1136ff` private `main`ga push qilindi; [CI run 39065413758](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758) `verify` hamda Docker build/start/health joblari bilan **success** bo‘ldi. Git staging tekshiruvida lokal API-key, model joblib, SQLite, benchmark/trening JSON fayllari ignore qilingani, maxfiy kalit/token patternlari topilmagani tasdiqlandi. Promotion gate’ga keyin qo‘shilgan ikkinchi shart — har ko‘rilmagan turda kamida 0,20 recall — `card_testing`ning 0 natijasini ham rad etadi; qayta bajarilgan 342-seed gate’da `promote=false`, to‘rttala tur minimum shartdan o‘tmadi. Bu sintetik xavfsizlik mezoni, bank qabul standarti emas. Yangi gate kodi mahalliy 3 test va Ruff’dan o‘tdi; keyingi Git push uchun CI alohida tekshiriladi.

### Qo‘shimcha nazorat — 2-push va noto‘g‘ri metrika himoyasi

`b6cb856` private `main`ga push qilindi; [CI run 39065624573](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065624573) `verify` va Docker build/health bilan **success**. Visibility `PRIVATE`, fork 0, collaborator faqat `shomatoff` deb tekshirildi. Gate’dagi keyingi tuzatish bo‘sh yoki `NaN`/cheksiz/noto‘g‘ri recallni rad etadi, chunki `NaN` oddiy taqqoslashdan sirg‘alib o‘tishi mumkin; 4 fokus test va Ruff lokal o‘tdi. Bu hali faqat sintetik laborant mezoni, faol v6 model o‘zgarmagan. Ushbu so‘nggi tuzatishning GitHub CI’si keyingi push’da tekshiriladi.

## 2026-10-18 yangi qo‘shimcha — besh bosqich, haqiqiy ULB va issiqlik nazorati

Oldingi “ULB bajarilmagan” yozuvlar o‘sha paytdagi holat bo‘lib saqlandi; **endi rasmiy Kaggle `mlg-ulb/creditcardfraud/versions/3` fayli Kaggle `kagglehub` orqali olinib, alohida benchmark bajarildi**. 284 807 qator, 492 fraud, 31 ustun va nol bo‘sh katak tekshirildi; SHA256 `76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89` — yuklangan nusxamizniki, upstream imzosi emas. Xronologik fit/validation/test 170 888 / 56 957 / 56 962; testda 75 fraud. Validation PR-AUC `.650727` logistic modelni tanladi; test PR-AUC `.696457`. Validation tanlagan threshold’da 114 alert, TP57/FP57/FN18/TN56 830, precision `.5`, recall `.76`. Retrospektiv exact-1% top-K’da 570 alert, TP65/FP505; bu deployment threshold’i emas. Idealizatsiyalangan perfect-label feedback tajribasi test PR-AUC `.696457 → .709455`, ammo haqiqiy tahlilchi feedbacki emas. Batafsil barcha kandidatlar, 0,5/1/5/10% hajmlar va xatarlar [BENCHMARK](docs/BENCHMARK.md) oxirida. CSV, JSON natija, model va kalitlar Git’ga yuborilmaydi; faol v6 sintetik modelga ULB modeli ko‘chirilmagan.

Birinchi benchmark urinishida eski threshold izlash har bir qiymatda butun confusion matrix’ni qayta hisoblab CPU’ni ~104% band qildi; foydalanuvchi qizishni sezgach jarayon to‘xtatildi. Algoritm teng ballarni guruhlab kumulyativ sanashga o‘tkazildi; eski exhaustive natija bilan testda teng. Qayta urinish `cpulimit -f -l 35` bilan tugadi, sensor CPU ~46°C atrofida qoldi. Bu xato va tuzatish kodda `fraud_detector/evaluation.py`, regressiya testi `tests/test_operations.py`da.

Qolgan 4 bosqich: (2) `card_testing`ning o‘tgan/joriy belgilardan tavsifiy ishorasi qo‘shildi, ML reytingi/threshold o‘zgarmadi; 742-seed 12 000 sintetik oqimda 142 ishora, 121 fraud, 21 non-fraud, `card_testing` fraudining 121/157 tasi topildi — noto‘g‘ri ijobiy sabab avtomatik bloklash yo‘q. (3) admin-only feedback summary `unknown`, `pending`, final status va 7 kunlik maturation’ni ajratadi; avtomatik training yo‘q. (4) sintetik ML top-K review queue va 1000 qatorlik monitoring qo‘shildi; jonli telemetry, versiyali backup yoki avtomatik rollback **yo‘q**. (5) lokal API score/batch/report-write/analytics chegaralari, `429 Retry-After`, admin auth va CVV/PIN/PAN kabi ortiqcha maydonlarni 422 rad etish sinovlari bor; ko‘p-process/gateway/bank RBAC emas. Tafsilot va manbalar [FIVE_STAGE_UPGRADE_UZ](docs/FIVE_STAGE_UPGRADE_UZ.md)da.

Lokal tekshiruv: **35 passed, 1 LightGBM SHAP tashqi warning**, Ruff toza, `pip-audit` “No known vulnerabilities found” (hozirgi vaqt uchun), repo `PRIVATE`. CI pushdan so‘ng alohida tasdiqlanadi. Qolgan xavf: tarixiy PCA ma’lumotidan bankga umumlashtirib bo‘lmaydi; haqiqiy tahlilchi yorliqlari, real vaqtli holdout, jonli monitoring, rollback mashqi, production auth/gateway, pentest va bank shadow sinovi hali yo‘q. Faol v6 modelni o‘zgartirmaslik qarori saqlandi.

### Besh bosqichning GitHub CI tasdig‘i

Kod, test va hujjatlar `eaab859` sifatida private `main`ga push qilindi. [CI run 39067304869](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39067304869) **success**: `verify` (Ruff, pytest, pip-audit, model treningi va 3-seed smoke) hamda `docker-build` (build, start, health) ikkalasi ham yashil. Git stagingda 144 MiB ULB CSV, benchmark JSON, API kalitlar, SQLite va joblib yo‘q; `data/public/` ignore qilingan. Ushbu CI qaydi hujjat-only keyingi pushda boradi; o‘sha push uchun status alohida tekshiriladi.

## 2026-10-18 keyingi qo‘shimcha — real bank oldidan umumlashish auditi

Oldingi besh bosqich hisoboti saqlandi. `scripts/audit_generalization.py` faqat yangi diagnostika: 842-seed, 30 000 sintetik voqea, 20% mijoz ID fit/validation'dan butunlay chetda, keyingi vaqt oynasida alohida baholash. Oddiy logistic validation PR-AUC `.701036` bilan tanlandi, threshold `.2226729131` ham faqat validationdan. Ko‘rilgan mijoz testida 4 747 qator/280 fraud: PR-AUC `.724427`, TP222/FP99/FN58/TN4368. Chetlatilgan mijoz testida 1 188 qator/55 fraud: PR-AUC `.739150`, TP47/FP25/FN8/TN1108. Sintetik **mijoz-holat** 5% sig‘imdagi top-K: ko‘rilganlarda 58/58 alert haqiqiy fraudli mijoz (jami 118), yangi kohortda 15 alertdan 14 tasi (jami 21). Bu retrospektiv, bank kartasi ID'si emas va streaming queue siyosati emas.

Qarshi dalillar yashirilmagan: ko‘rilgan kohortdagi 124 qonuniy `legit_many_declines`dan 18 noto‘g‘ri alert (14,5%); yangi kohortda `card_testing` 25 positive va `legit_many_declines` 20 negative bo‘lgani uchun ularga ishonchli segment ulushi chiqarilmadi. Dastlabki hisobda “ko‘rilgan” kohortga 65 hali ko‘rilmagan qator tushgani aniqlanib, faqat rivojlanish davrida mavjud mijozlar qoladigan qilib tuzatildi va qayta hisoblandi. Bitta seed va o‘sha generator bilan yuqori ko‘rsatkich real bankga umumlashishni isbotlamaydi; darhol mavjud sintetik label kechikkan real yorliqni ham aks ettirmaydi. Faol model **o‘zgarmadi**, testga qarab tuning qilinmadi. Protokol va ruxsatli data, shadow, monitoring/rollback, production security uchun aniq **NOT DONE** darvozalari [GENERALIZATION_AND_READINESS_UZ](docs/GENERALIZATION_AND_READINESS_UZ.md)da. Eskirgan ULB reja holatiga [AI_TRAINING_ROADMAP_UZ](docs/AI_TRAINING_ROADMAP_UZ.md) oxirida qo‘shimcha kiritildi. Lokal **39 passed, 1 SHAP warning**, Ruff toza; GitHub push/CI keyin alohida qayd etiladi.

### Customer-disjoint audit CI qaydi

`4357fce` private `main`ga yuborildi va [Actions run 39067893435](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39067893435) **success**: `verify` (Ruff, 39 test, audit, model treningi, 3-seed smoke) va Docker build/start/health joblari yashil. Lokal `data/generalization_audit.json` Git'ga qo‘shilmadi; faol v6 artifact yangilanmadi. Ushbu CI qaydi hujjat-only keyingi push bilan qo‘shiladi.

## 2026-10-18 qo‘shimcha — dashboard imkoniyatlarini ochiq ko‘rsatish

Eski besh sahifa saqlanib, uch yangi ko‘rinish qo‘shildi: model bahosiga ko‘ra saralangan 5/10/20/50/100 sig‘imli sintetik **Tekshiruv navbati**, qat’iy 1000 qatorli demo alertlari va tarixiy PSI diagnostikali **Operatsiyalar**, hamda 11 imkoniyatni `lokal demo`/`faqat tadqiqot`/`mavjud emas` deb ajratuvchi **Imkoniyatlar** xaritasi. Overview’da ularga tezkor yo‘llar bor; hisobot jadvalida endi analyst statusi ham ko‘rinadi. Admin-only feedback xulosasi `unknown`, `pending`, `confirmed_fraud`, `analyst_false_positive` va 7-kunlik `matured_eligible` hisoblarini ko‘rsatadi; admin kaliti yangi UI’da saqlanmaydi, so‘rovdan keyin maydon tozalanadi, sahifadan chiqishda xulosa ham o‘chadi. Ingliz, o‘zbek va rus tarjimalari hamda mobil layout yangilandi.

Chegara ataylab ko‘rinadigan qilib yozildi: navbat to‘lovni bloklamaydi, card-testing ishorasi reytingga ta’sir qilmaydi, monitoring jonli bank telemetriyasi emas, feedback avtomatik trening yoki production label tasdig‘i emas; real bank integratsiyasi, production RBAC va avtomatik rollback mavjud emas. Faol v6 model/threshold, API va data o‘zgartirilmadi. To‘liq lokal tekshiruv: **39 passed, 1 tashqi SHAP warning**, Ruff toza, JS sintaksisi toza; Chrome live-smoke’da uch til, 20→5 navbat, monitoring/drift, admin feedback, 11 karta va 390px mobil layout o‘tdi. GitHub push/CI natijasi keyingi qo‘shimchada alohida yoziladi.

### Dashboard GitHub CI tasdig‘i

Dashboard kod/test/hujjatlari `33b491f` commit sifatida private `main`ga push qilindi. [Actions run 39068636423](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39068636423) **success**: `verify` (Ruff, pytest, pip-audit, model treningi, 3-seed smoke) va `docker-build` (build/start/health) o‘tdi. Maxfiy kalit, model artifact, SQLite yoki ULB CSV commitga kiritilmadi. CI brauzer smoke’ni o‘z ichiga olmaydi; Chrome testi lokal bajarildi.
