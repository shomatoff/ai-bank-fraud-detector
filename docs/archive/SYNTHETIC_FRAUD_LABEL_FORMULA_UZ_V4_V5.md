# Sintetik firibgarlik yorlig‘i formulasi — O‘zbekcha (v4)

## Joriy v5-local formula (quyidagi v4 matni tarixiy)

Tenglama o‘zgarmagan: `is_fraud_i = 1{U_i < p(scenario_i)}`, bu yerda `U_i ~ Uniform[0,1)` mustaqil olinadi. To‘rtta firibgarlikka o‘xshash ssenariyda endi `p=.88` (12% manfiy yorliq shovqini), `legit_travel` va `legit_large_purchase`da `.01`, yangi `legit_many_declines`da `.02`, oddiy holatda `.01` (ilgari `.005`). Yangi qonuniy holat reja bo‘yicha 2,5% qatorni beshtalik epizodlarda beradi: onlayn elektronika, summa 100–1 800, rad etilish ehtimoli .85, yangi qurilma .50, sun’iy country-risk taqsimoti .2/.6/.2. Demak, oldingi radlar ko‘p bo‘lsa ham har bir voqea firibgarlik deb belgilanmaydi. Normalni qo‘shib sakkiz ssenariy bor. Bular inson haqidagi dalil emas, simulyator parametrlari. 20% kalibrlash bo‘lagida Platt sinaladi, lekin validation Brier **va** ECE ikkalasi yaxshilanmasa o‘chiriladi; joriy v5 xom logistik ehtimolni ishlatadi. [v5 natijalari](MODEL_EVALUATION.md#v5-local-rigor-audit-2026-10-15).

## Tarixiy v4 formula va misollar

Bu formula **simulyatsiya yorlig‘ini yaratadi**, inson firibgarlik qilganini isbotlamaydi. Avvalgi v3 dagi `Bernoulli(sigmoid(z))` formulasi v4 da **ishlatilmaydi**. Havolalar: [English](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md), [Русский](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md), [ssenariylar](SYNTHETIC_SCENARIOS.md), [baholash](MODEL_EVALUATION.md), [imkoniyatlar auditi](FRAUD_DETECTION_CAPABILITIES.md).

Avval `generate_event_stream(count, seed, start)` har bir rejalangan epizodga yetti ssenariydan birini beradi. Firibgarlikka o‘xshash `account_takeover`, `card_testing`, `mule_cashout`, `new_account_transfer` ssenariylarining har biri taxminan 1,5% qatorni tashkil etadi. Qonuniy sayohat va yirik xarid holatlarining har biri taxminan 2,5%; qolganlari `normal`. Epizodlar butun bo‘lishi sababli aniq sonlar yaxlitlanadi. Har bir ssenariy sintetik belgilar oralig‘ini o‘zgartiradi: masalan, card testing — ko‘p kichik onlayn to‘lov va rad etishlar; qonuniy sayohatda ham yangi qurilma, uzoq masofa va yuqori xavf darajasi bo‘lishi mumkin. To‘liq parametrlar [jadvalda](SYNTHETIC_SCENARIOS.md).

Har bir `i` qator uchun yangi tasodifiy `U_i ~ Uniform[0,1)` olinadi va

`is_fraud_i = 1, agar U_i < p(scenario_i); aks holda 0`.

Bu yerda to‘rtta firibgarlik ssenariysi uchun `p=0.94`, ikki qonuniy murakkab holat uchun `p=0.01`, oddiy holat uchun `p=0.005`. Bu ehtimollar **bank statistikasi emas**, generator muallifi tanlagan shovqin parametrlaridir. Misol: card testing qatorida `U=.20` bo‘lsa `.20<.94` sababli yorliq 1, `U=.97` bo‘lsa yorliq 0. Sayohatda `U=.50` bo‘lsa yorliq 0, `U=.005` bo‘lsa shovqinli yorliq 1. Bu sonlar formulani tushuntiruvchi misollar; bajarilgan datasetdagi aynan shu tasodifiy qiymatlar deb da’vo qilinmaydi. Haqiqiy seeded-run ulushi alohida o‘lchanadi.

`velocity_1h` ayni sintetik mijozning faqat oldingi bir soatdagi voqealarini sanaydi; `prior_declines_24h` faqat oldingi 24 soatdagi alohida simulyatsiya qilingan rad etishlarni sanaydi. Joriy/kelajak voqealari va firibgarlik yorlig‘i hisobga kirmaydi. Ssenariy nomi va mijoz ID modelga berilmaydi. Logistik model o‘n belgi bo‘yicha **boshqa, o‘rganilgan** tenglamani tuzadi va alohida ma’lumotda Platt kalibrlashini qo‘llaydi. Uning bali ssenariyning `p` qiymati ham, real bank ehtimoli ham emas. Eng katta chiziqli hissalar hisobni tushuntiradi, firibgarlik sababini emas. Inson ishonchi yorliq formulasining o‘zidan emas, manba shaffofligi, ajratilgan testdagi xatolar, ekspert ko‘rigi va cheklovlarni bilishdan kelishi kerak.
