# AI modelini yaxshilash tajribasi — halol natija va promotion qarori

Sana: 2026-10-18. **Faol model: v6; interaction challenger production/app modeliga chiqarilmadi.** Barcha quyidagi raqamlar faqat loyiha generatoridagi sintetik ma’lumotlarga tegishli. Real bank aniqligi, tayyorligi yoki xavfsizligini isbotlamaydi.

## Maqsad va oldindan belgilangan protokol

Joriy 10 belgi asosida to‘rtta voqea paytida ma’lum bo‘ladigan interaction qo‘shildi: kichik onlayn xarid × yangi qurilma, kichik summa × oldingi 1 soat velocity, yangi qurilma × velocity, yosh hisob × transfer. `scenario`, `is_fraud`, mijoz ID’si va keyingi voqealar modelga kiritilmadi. Logistic pipeline va izohlash imkoniyati saqlandi; u alohida `interaction_candidate()` sifatida turadi, faol `candidates()` ro‘yxatida emas.

`scripts/evaluate_interaction_challenger.py` avval 142–146 development seedlari va ulardan mustaqil 500145–500149 test seedlarida sinov o‘tkazdi. Shu natijadan so‘ng 5% alert aniqligi asosidagi validation-selection qoidasi belgilandi; **yangi** 242–251 development va 500245–500254 test seedlari bilan 10-seed tasdiqlash o‘tkazildi. Har development to‘plami 12 000 satr, fit 7 200, validation 2 400; har test 3 000 satr. Exact 5% natija har testda 150 eng yuqori score bo‘yicha retrospektiv hisoblanadi; bu live threshold emas.

| Mustaqil 10-seed tasdiq (sintetik) | Eski validation-PR-AUC baseline | Validation’da tanlangan yangi siyosat |
|---|---:|---:|
| Test PR-AUC o‘rtacha | 0,7566 | 0,7680 |
| Exact 5% precision o‘rtacha | 0,8360 | 0,8653 |
| Exact 5% recall o‘rtacha | 0,6703 | 0,6938 |

Yangi siyosat 10 seeddan 9 tasida interaction challenger’ni tanladi. Bu raqamlar `data/challenger_confirmation.json`da (faqat lokal, Git’da ignore); ularga ishonch oralig‘i yoki bank generalizatsiyasi da’vo qilinmaydi. Dastlabki 5-seed sinovda exact-5% precision 0,8133 → 0,8480 bo‘lsa ham, PR-AUC 0,7698 → 0,7691 pasaygan edi — shuning uchun bitta metrika bilan qaror qilinmadi.

## Nega faol modelga chiqarilmadi

`scripts/heldout_promotion_gate.py` *alohida* development seed 342 va May test seed 900345 bilan to‘rtta fraud turini navbatma-navbat fit va validation’dan to‘liq chiqaradi. Har turda baseline va challenger threshold’i faqat qolgan ma’lum turlar validation yorliqlarida tanlanadi; o‘sha tur faqat oxirgi baholashda ko‘riladi. Promotion mezoni: birorta tur recall’i baseline’dan 0,05 absolutdan ortiq pasaymasin. Bu sinov promotion validatsiyasi, endi undan keyingi “untouched final test” emas.

| Ko‘rilmagan tur | Pozitivlar | Baseline recall | Challenger recall | Qaror |
|---|---:|---:|---:|---|
| Account takeover | 399 | 0,4887 | 0 | regressiya |
| Card testing | 400 | 0 | 0 | ikkisi ham muvaffaqiyatsiz |
| Mule/cash-out | 395 | 0,9165 | 0,1671 | regressiya |
| New-account transfer | 400 | 0,5500 | 0 | regressiya |

`data/heldout_promotion_gate.json` (lokal) `promote=false` va uchta muvaffaqiyatsiz turni qayd etadi. Shu bois v7 sinov artefakti ishlab turgan v6 o‘rniga qo‘yilmadi; `ARTIFACT_VERSION=6`, faol model tanlovi avvalgidek. v7 bo‘yicha eski 42–51 test seedlariga qayta qarash ham bajarilgan (`data/v7_evaluation.json`), ammo bu seedlar v6 auditida allaqachon ko‘rilgani uchun u **mustaqil tasdiq emas** va modelni chiqarish uchun ishlatilmadi. Birinchi holdout diagnostikasida v7 PR-AUC selection bilan aynan deployment selection mos kelmagani aniqlandi; keyin mos 5% selection bilan qayta sinovda ham jiddiy pasayish saqlanib qoldi. Bu xato/cheklov yashirilmaydi.

## Tashqi data va bank darajasiga yetish uchun qolgan shartlar

Rasmiy [ULB/Worldline dataset sahifasi](https://www.kaggle.com/mlg-ulb/creditcardfraud/) 284 807 tranzaksiya va 492 fraudni tasvirlaydi. Rasmiy Kaggle API download URL bu muhitda 2026-10-18 kuni HTTP 404 qaytardi, mahalliy Kaggle credentials va asl CSV yo‘q. Hech qanday uchinchi tomon mirror’i asl manba sifatida olinmadi; ULB real benchmark **bajarilmadi**. Litsenziyali asl CSV + checksum olingach, mavjud alohida benchmark pipeline ishga tushirilishi kerak. [ULB fraud-detection handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html) vaqt bo‘yicha baholash va fraud label kechikishini, [top-k bo‘limi](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/TopKBased.html) esa analitik sig‘imini alohida ko‘rib chiqishni tavsiya qiladi.

Haqiqiy bank darajasini faqat ruxsatli real data, delayed/unknown label siyosati, privacy va xavfsizlik nazorati, mustaqil tekshiruv, shadow-mode monitoring va real operatsion xato qiymati bilan baholash mumkin. Sintetik natijadan “dunyo banklari bilan teng” degan xulosa chiqmaydi. GitHub repo private qilish ham ilgari public bo‘lgan davrdagi nusxalar/cachelarga kafolat bermaydi.

## Tekshiruv va qayta bajarish

```bash
.venv/bin/python -m scripts.evaluate_interaction_challenger --first-seed 242 --seeds 10 --output data/challenger_confirmation.json
.venv/bin/python -m scripts.heldout_promotion_gate --seed 342 --output data/heldout_promotion_gate.json
.venv/bin/pytest -q
.venv/bin/ruff check fraud_detector tests scripts
```

Joriy ishda pytest **29 passed, 1 tashqi SHAP warning**, Ruff **clean**. `tests/test_interaction_challenger.py` nomzodning yorliq/scenario/metadataga qaramasligini, score chegarasini, faol ro‘yxatdan tashqarida qolishini va regressiya gate’i rad etishini tekshiradi. `data/`dagi model, natija JSON, API-key, SQLite va CSV Git’da ignore qilinadi; ulardan hech biri GitHub’ga yuborilmaydi.

## Qo‘shimcha xavfsizlik sharti va GitHub tasdig‘i

Promotion gate dastlab baseline’dan 0,05 absolutdan ortiq recall pasayishini rad etardi. **Qo‘shimcha qat’iy shart** sifatida endi har ko‘rilmagan turda kamida 0,20 recall talab etiladi; bu baseline ham challenger ham 0 bo‘lgan `card_testing`ni xato “o‘tdi” deb belgilamaslik uchun kiritildi. Qayta bajarilgan 342-seed gate: `promote=false`; regression failures — `account_takeover`, `mule_cashout`, `new_account_transfer`; minimum-recall failures — **to‘rtala tur**. 0,20 sintetik safety-screen mezoni, bankning operatsion qabul chegarasi emas.

`d1136ff` commit private `main`ga push qilindi. [GitHub Actions CI run](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065413758) `verify` va Docker build/health joblarida **success** bo‘ldi. Bu run keyingi 0,20 shartli kichik commitdan **oldingi** holatni tekshirgan; yangi commit uchun alohida run tasdiqlanadi. Repo visibility `PRIVATE`/`isPrivate=true` qayta tekshirildi.

Keyingi `b6cb856` commitdagi qat’iy 0,20 shart ham [CI run 39065624573](https://github.com/shomatoff/ai-bank-fraud-detector/actions/runs/39065624573)da `verify` va Docker bilan **success** bo‘ldi. Gate’ning navbatdagi kichik himoyasi bo‘sh, `NaN`/cheksiz yoki [0,1]dan tashqari recall/chegaralarni `ValueError` bilan rad etadi; `NaN` taqqoslashni aylanib o‘tib modelni xato promote qila olmaydi. Bu yangi kirish-validatsiya o‘zgarishi mahalliy 4 ta fokus test va Ruff’da tekshirildi; yangi push CI’si alohida ko‘riladi.
