# Yangi mijoz diagnostikasi va haqiqiy tizimga o'tish darvozalari

Sana: 2026-10-18. Bu **sintetik, alohida diagnostika**, faol v6 modelni almashtirish yoki bankka deploy qilish qarori emas.

## Bajarilgan diagnostika

`scripts.audit_generalization` 842-seed bilan 30 000 xronologik sintetik voqeani ishlatdi. 20% `customer_id` butunlay fit/validation'dan chetlatildi; fit 60%, validation 20%, test keyingi 20% vaqt oynasida. Boshqa 80% ichidan ham faqat fit yoki validation'da haqiqatan ko'rilgan mijozlar `seen_test`ga kirdi. `customer_id`, `scenario`, `event_time` va label **model belgilari emas**. Model turi validation PR-AUC bilan, threshold validation xarajati/10% sig'im bilan tanlandi; test natijasiga qarab qayta sozlanmadi. Avvalgi dastlabki hisobda `seen_test`ga rivojlanish oynasida hali uchramagan 65 qator ham kirgani sezilib, kohort ta'rifi tuzatildi va quyidagi yakuniy diagnostika qayta bajarildi.

```bash
cpulimit -f -l 35 -- .venv/bin/python -m scripts.audit_generalization \
  --seed 842 --rows 30000 --output data/generalization_audit.json
```

Validation PR-AUC: oddiy logistic `.701036`, regularized logistic `.697632`; birinchisi tanlandi. Tanlangan threshold `.2226729131`. Test qiymatlari:

| Kohort | Tranzaksiya/fraud | PR-AUC | Threshold TP/FP/FN/TN | Precision/recall | 5% mijoz holati top-K |
|---|---:|---:|---:|---:|---:|
| Oldin ko'rilgan mijozlar | 4 747 / 280 | .724427 | 222/99/58/4368 | .6916 / .7929 | 58/58 topilgan; 118 fraudli mijozdan 58 |
| Fit/validation'dan chetlatilgan mijozlar | 1 188 / 55 | .739150 | 47/25/8/1108 | .6528 / .8545 | 15 o'rindan 14 fraudli mijoz; jami 21 fraudli mijoz |

Mijoz top-K faqat **retrospektiv** diagnostika: sintetik mijozning barcha test voqeasidagi eng yuqori balli va hech bo'lmasa bitta fraud yorlig'i bilan bir holat hisoblanadi. Real karta/akkaunt ID'si, vaqtli navbat siyosati yoki bank mijozlari yo'q. [Fraud Detection Handbook](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_4_PerformanceMetrics/TopKBased.html) holat/karta top-K mezonining sababini tushuntiradi.

Muhim qarshi dalil: ko'rilgan kohortdagi `legit_many_declines`ning 124 **qonuniy** voqeasidan 18 tasi noto'g'ri alert (14,5%). Yangi mijoz kohortida `card_testing` 25 positive va `legit_many_declines` 20 negative — **30 tadan kam**, shu sabab ularning segment recall/false-alert ulushi xulosa sifatida berilmaydi. Ko'rilgan kohortda `card_testing` 44/54 aniqlangan, lekin bu generatorning treningda tanish naqshi; ilgari butun typology holdout sinovida juda yomon natija chiqqanini inkor etmaydi. Bitta seed, bitta generator va darhol ma'lum sintetik yorliqlar bilan olingan natija real bankga ko'chmaydi. Test ko'rildi; shu testga qarab modelni o'zgartirish uchun **yangi mustaqil holdout** zarur. [Vaqtli/kechikkan yorliq validatsiyasi](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html), [data leakage](https://scikit-learn.org/stable/common_pitfalls.html).

## Keyingi go/no-go darvozalari

| Bosqich | Hozirgi holat | O'tish uchun zarur dalil |
|---|---|---|
| 1. Ruxsatli real data | **YO'Q** | Ma'lumot egasi vakolati, foydalanish maqsadi, saqlash muddati, minimallashtirilgan event/feature va label mavjudlik vaqti; PAN/CVV/PIN olinmasligi. ULB tarixiy benchmark buning o'rni emas. |
| 2. Mustaqil baholash | **QISMAN, faqat sintetik** | Oldindan muzlatilgan keyingi vaqt oralig'i, customer-disjoint va yangi naqsh holdout, yetarli segment soni, kechikkan/unknown label embargo, tahlilchi sig'imidagi case-level TP/FP va kalibrlash. Qabul chegaralarini bank risk egasi **testni ko'rishdan oldin** belgilashi kerak. |
| 3. Shadow rejim | **YO'Q** | Vakolatli tashkilotda faqat kuzatuvchi, to'lov qaroriga ta'sirsiz integratsiya; kirish nazorati, rozilik/huquqiy ko'rik, xavfsiz telemetry, human review va incident kanali. Bizda real bank API yoki ruxsat yo'q; ulanish qilinmaydi. |
| 4. Monitoring/rollback | **QISMAN, sintetik monitoring** | Jonli drift, kalibrlash, alert sig'imi, false-positive, latency va xizmat xatolari; oldindan kelishilgan alert va operator; versiyalangan ishonchli artifact/backup, tekshirilgan restore, qaytarish mashqi va audit izi. Hozirgi HMAC bitta lokal trust root xolos. |
| 5. Production xavfsizlik | **YO'Q** | Tashkilot identifikatsiyasi va obyekt/funksiya darajasida auth, markaziy limit, secrets management, transport/shifrlash, audit, threat model, mustaqil pentest va amaldagi to'lov ma'lumoti talablari. Mahalliy API key va IP limiti yetmaydi. |

Bu mezonlar NIST [AI RMF](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)ning mustaqil baholash, monitoring, qaytarish va incident boshqaruvi yo'nalishlariga hamda [OWASP API Security Top 10](https://api-security.owasp.org/editions/2023/en/0x11-t10/)dagi auth/obyekt/resource xavflariga mos tavsiyalardir, **bank sertifikati yoki avtomatik compliance emas**. [PCI SSC](https://www.pcisecuritystandards.org/faqs/1533/) CVV/PIN kabi sensitive authentication data'ni avtorizatsiyadan keyin saqlashga yo'l qo'ymasligini izohlaydi.
