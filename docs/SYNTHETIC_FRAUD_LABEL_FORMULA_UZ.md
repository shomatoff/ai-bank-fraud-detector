# Sintetik firibgarlik yorlig‘i formulasi — joriy v6

Har bir `i` voqeada generator mustaqil `U_i ~ Uniform[0,1)` sonini oladi va quyidagicha belgilaydi:

`is_fraud_i = 1{U_i < p(scenario_i)}`.

To‘rtta firibgarlikka o‘xshash ssenariyda `p=.88`; qonuniy sayohat va yirik xaridda `.01`; qonuniy ko‘p rad etilishda `.02`; oddiy voqeada `.01`. Masalan, **faqat tushuntirish uchun** card-testing qatorida `U=.20` bo‘lsa yorliq 1, `U=.97` bo‘lsa 0. Bu qiymatlar bajarilgan datasetdagi aniq tasodifiy sonlar deb da’vo qilinmaydi. Fraud ssenariydagi 12% manfiy shovqin va qolganidagi ijobiy shovqin muallif tanlagan simulyator parametridir — bank statistikasi yoki inson aybining dalili emas.

V6 barcha epizodlarni 30 kunlik simulyatsiyaning davomiga tarqatadi; yangi hisob yoshi aynan voqea vaqtida aniqlanadi. Soatlik faollik va 24 soatlik radlar faqat shu sintetik mijozning **oldingi** voqealaridan hisoblanadi. Ssenariy, mijoz ID, vaqt, rad belgisi va yorliq modelga kiritilmaydi. O‘rganilgan logistik baho generatorning `p` qiymati emas; chiziqli hissalar sababiy xulosa bermaydi. `p=.88` bo‘lganda faqat fraud ssenariylarni tanlagan exact-top-k precisionning **kutilgan taxminiy** chegarasi `.88` atrofida, lekin yakuniy namuna uchun qat’iy limit emas. [Parametrlar](SYNTHETIC_SCENARIOS.md) · [joriy baholash](MODEL_EVALUATION.md) · [tarixiy izoh](archive/SYNTHETIC_FRAUD_LABEL_FORMULA_UZ_V4_V5.md).
