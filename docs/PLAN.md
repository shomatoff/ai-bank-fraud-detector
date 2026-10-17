# Verification plan

1. Read the original master prompt without editing it and inventory code, docs, screenshots, tests and CI. **Done.**
2. Run the existing test/lint commands and record actual failures. **Done; pytest initially needed the local package path.**
3. Add the three requested regression areas without weakening requirements. **Done; focused tests pass.**
4. Document the implemented architecture, data limits, security, testing, local deployment, changelog and social-asset process. **Done.**
5. Complete the numbered 0–14 gap matrix with file/log evidence and explicit deviations. **Done.**
6. Run full pytest and Ruff, then record exact results in the gap analysis. **Done: 26 passed; Ruff clean.**

This plan deliberately excludes GitHub pushes, tags/releases and social publication; those require separate explicit approval under the master prompt.

## AI o‘qitish bo‘yicha keyingi ish (2026-10-18)

1. Mavjud v6 generator, training split, data/provenance va manbalarni tekshirish — **bajarildi**, natija [AI_TRAINING_ROADMAP_UZ](AI_TRAINING_ROADMAP_UZ.md)da.
2. Asl ULB CSV uchun manba, litsenziya va checksumni tasdiqlash — **kutilmoqda; fayl hozir lokalda yo‘q**.
3. Alohida ULB benchmark, keyin mos shartlarda PaySim/IEEE-CIS sinovlari — **kutilmoqda**.
4. Yangi ssenariy/customer holdout va mustaqil baholash — **kutilmoqda**.

## 2026-10-18 qo‘shimcha bosqich holati

5. Sintetik interaction challenger va 5+10 yangi seedda tasdiqlash — **bajarildi**; odatiy 5% top-k yaxshilandi, [to‘liq dalil](AI_CHALLENGER_EVALUATION_UZ.md)da.
6. Boshqa seedda to‘rtta held-out fraud turiga promotion gate — **bajarildi; FAILED**, uch turdagi katta recall regressiyasi tufayli faol v6 model saqlandi. `tests/test_interaction_challenger.py` qayta tasodifiy chiqarib yuborishni to‘sadi.
7. Asl ULB CSV, checksum, alohida public benchmark — **kutilmoqda**; rasmiy download 404, fayl va Kaggle credentials yo‘q. Uchinchi tomon mirror ishlatilmadi.
8. Ruxsatli real bank/shadow sinovi, delayed labels, privacy va mustaqil audit — **bajarilmagan**; bu loyiha bank darajasida deb e’lon qilinmaydi.
9. Promotion gate’ni yomonlashmaslik + minimal holdout recall + finite input nazorati bilan mustahkamlash — **bajarildi**; faol modelni chiqarish hali `promote=false`.
