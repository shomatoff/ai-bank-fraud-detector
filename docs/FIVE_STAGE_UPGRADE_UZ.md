# Besh bosqichli ehtiyotkor takomillashtirish — 2026-10-18

Bu hujjat oldingi hisobotlarni almashtirmaydi. Har bir natija laboratoriya doirasida; haqiqiy bank xavfsizligi, mijoz ma'lumotlari yoki ishlab chiqarishdagi samaradorlik da'vo qilinmaydi. Faol v6 model va uning threshold'i o'zgartirilmagan.

## 1. Rasmiy ULB benchmark

Rasmiy [Kaggle ULB/Worldline sahifasi](https://www.kaggle.com/mlg-ulb/creditcardfraud/data) va [Kaggle'ning `kagglehub` vositasi](https://github.com/Kaggle/kagglehub) orqali `mlg-ulb/creditcardfraud/versions/3` dagi `creditcard.csv` yuklandi. Mahalliy nusxa `data/public/ulb-v3/creditcard.csv` ichida va `.gitignore` bilan Git'dan chetlatilgan. Lokal SHA256 `76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89`; 284 807 qator, 31 ustun, 492 fraud yorliq, `Time` 0–172792, bo'sh qiymat 0. Bu digest **mahalliy yuklangan faylga** tegishli; upstream imzosi yoki boshqa manbadan mustaqil provenance kafolati emas. Rasmiy sahifadagi foydalanish shartlarini amalda qayta tekshirish kerak.

`scripts.run_public_benchmark` aynan shu digest bilan xronologik 60/20/20 split, validation orqali model/threshold tanlash va bir martalik testni bajardi; natijalar [BENCHMARK](BENCHMARK.md) oxiriga qo'shildi. Bu modelning `V1`–`V28` PCA belgilari lokal dasturning 10 belgisi bilan mos emas: benchmark alohida tadqiqot, lokal API'ga almashtirish emas. Vaqt oralig'i ikki kun, bitta tarixiy manba, haqiqiy bank yoki bugungi tahdidlar uchun ishonchli tashqi tasdiq yo'q.

## 2. `card_testing` uchun ikkilamchi ko'rik ishorasi

`possible_card_testing_burst` faqat mavjud past/joriy belgilar (`amount <= 30`, `online`, yangi qurilma va oldingi tezlik yoki rad etish) bilan tavsifiy ishora beradi. U model ehtimoli, navbat reytingi, `review_recommended` yoki avtomatik to'lov qarorini o'zgartirmaydi. `GET /api/review-queue` ishorani ko'rsatadi; `POST /api/score` da `secondary_hint_changes_model_decision=false`.

Mustaqil 742-seed, 12 000 qatorlik **sintetik** oqimda ishora 142 marta: 121 fraud, 21 non-fraud. `card_testing` 157 frauddan 121 tasi (77,1%) ishoralangan; 36 tasi o'tkazib yuborilgan. 180 ta `card_testing` epizodining 20 tasi non-fraud bo'lsa, ishoraning 141 tasidan 20 tasi shu turdagi legitim holat; yana 1 tasi normal oqimdan. Bu qoida modelga qo'shilmagan va boshqa turdagi fraud uchun recall bermaydi. Qasddan yaratilgan past summali legitim online/new-device holat ham ishoralanishi testda ko'rsatilgan: avtomatik bloklashga yaramaydi. Oldingi interaction challenger typology gate'dan o'tmagani uchun rad etilgan.

## 3. Kechikkan va noma'lum yorliqlar

`GET /api/feedback/summary` faqat admin kaliti bilan: yangi xabarni `unknown`, ko'rib chiqilayotganini `pending`, tahlilchi `confirmed_fraud`/`false_positive` holatini alohida sanaydi. Yakuniy holat so'nggi yangilanganidan kamida 7 kun o'tgan bo'lsagina `matured_eligible` hisoblanadi; vaqt UTC va tartibli bo'lishi shart. Bu faqat **laboratoriya tahlilchisi statusi**: bankning qaytarilgan to'lov, tekshiruv yoki uzil-kesil haqiqat yorlig'i emas. Avtomatik qayta o'qitish yo'q; noto'g'ri ijobiy yoki soxta tasdiq trainingga o'tkazilmaydi. Kechikkan yorliqlar va vaqtli validation zarurati [Fraud Detection Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html) bilan asoslangan.

## 4. Tahlilchi sig'imi, monitoring va rollback chegarasi

`GET /api/review-queue?capacity=20` 1–100 oralig'idagi aniq top-K qatorni **faqat ML probability** bo'yicha saralaydi; ishora reytingga ta'sir qilmaydi. Qaytgan `SYN-*` identifikatorlar faqat ko'rsatmali, real hisob yoki karta identifikatori yo'q. `GET /api/monitoring` qat'iy 1000-qatorlik sintetik namunaning threshold alert soni/ulushi va avvalgi validation/test diagnostikasini beradi; jonli telemetriya emas. Exact top-K va review budgetning amaliy ma'nosi [Fraud Detection Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/TopKBased.html) bilan mos.

Rollback **avtomatik emas**. Agar keyinchalik haqiqiy deployda drift, kalibrlash, kechikish, review sig'imi yoki typology regressiyasi aniqlansa, operator oqimni to'xtatishi, oxirgi tekshirilgan artifact + uning checksum/HMAC'ini tashqi ishonchli nusxadan tiklashi, mustaqil tasdiq va qayta ishga tushirishdan oldin tekshirishi kerak. Hozir versiyalangan backup, real telemetry, alerting, operator runbook mashqi va shadow deployment yo'q. Shu sabab bosqich **qisman**; production rollback deyish noto'g'ri. NIST [AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) doimiy monitoring va xavfni boshqarishni talab etuvchi yondashuv uchun manba.

## 5. API xavfsizligi

Loopback demo'da score 120/min, CSV batch 10/min, report write 60/min, hisoblashga og'ir analytics 30/min (client IP + scope bo'yicha, bitta process ichidagi sliding window) cheklovi va `429 Retry-After` qo'shildi. Admin feedback summary admin kalitini talab qiladi. `Transaction` Pydantic `extra=forbid` bilan CVV, PIN, PAN va boshqa ortiqcha maydonlarni 422 bilan rad etadi; yangi testlar buni tekshiradi. Reportlarda mavjud CSRF, analyst/admin ajratilishi va obyekt GET/eksport auth'i saqlanadi. [OWASP API4](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/) limit zaruratini, [PCI SSC FAQ 1533](https://www.pcisecuritystandards.org/faqs/1533/) sensitive authentication data saqlanmasligini tushuntiradi.

Bu **faqat bir processli mahalliy mudofaa**: qayta ishga tushsa hisoblagich tozalanadi, ko'p worker orasida ulashilmaydi, IP NAT ortida umumiy bo'lishi mumkin. `Host` tekshiruvi tarmoqqa noto'g'ri bind qilishni xavfsiz qilmaydi; serverni faqat `127.0.0.1`ga bog'lash zarur. Keng tarmoq yoki bank mijozlari uchun gateway, markaziy rate limit, haqiqiy identifikatsiya/RBAC, audit, secrets manager, pentest va PCI talablari hali bajarilmagan.

## Tekshiruv va keyingi mezonlar

`tests/test_operations.py` ishora noto'g'ri ijobiysi, ML-only navbat tartibi, unknown/pending/maturation, limiter oynasi va mijoz ajratilishi, API auth, maxfiy maydon rad etilishi hamda 429 ni tekshiradi. Benchmark natijasi va CI tasdig'i alohida qo'shimcha sifatida yoziladi. Keyingi model promotion faqat oldindan muzlatilgan real vaqtli holdout, kalibrlash, segmentlar, kechikkan yorliqlar, capacity va mustaqil bank shadow sinovidan so'ng ko'rib chiqilishi mumkin.

### 1-bosqich yakuniy o'lchovi

Benchmark muvaffaqiyatli tugadi. Validation PR-AUC bo'yicha logistic tanlandi (`.650727`); undan keyingi 56 962 qatorlik testda 75 fraud bor, PR-AUC `.696457`. Validation tanlagan threshold 114 alertda TP57/FP57/FN18/TN56 830, precision `.5000`, recall `.7600` berdi. Exact 1% retrospektiv top-K (570 alert) TP65/FP505; bu real vaqt cutoff'i emas. Tarixiy ULB natijasini lokal v6 sintetik API'ga ko'chirish yoki umumiy bank samaradorligi deb talqin qilish mumkin emas. To'liq raqamlar va protokol [BENCHMARK](BENCHMARK.md) oxirida.
