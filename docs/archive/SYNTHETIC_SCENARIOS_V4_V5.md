# Synthetic scenario and label specification (v4)

## Current v5-local changes

The episode/share and feature construction below still apply except the additional `legit_many_declines` scenario: planned 2.5% share, five-event episodes, online electronics, amount 100–1,800, decline chance .85, new-device chance .50, artificial country-risk probabilities .2/.6/.2. Fraud-scenario positive-label probability is now `.88` (not `.94`); travel and large purchase remain `.01`; many declines is `.02`; normal is `.01` (not `.005`). These probabilities are generator assumptions and create harder ambiguous cases. Development uses chronological 60% fit / 20% calibration / 20% validation and an independent later synthetic test. Current [label formula EN](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md) / [UZ](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md) / [RU](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md) and [v5 evaluation](MODEL_EVALUATION.md#v5-local-rigor-audit-2026-10-15) supersede the historical v4 table below.

## Archived v4 specification

This document describes **simulation assumptions, not banking facts**. See [capabilities](FRAUD_DETECTION_CAPABILITIES.md), [model evaluation](MODEL_EVALUATION.md), and the language-specific label explanations: [English](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md), [O‘zbek](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md), [Русский](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md).

`generate_event_stream(count, seed, start)` fixes a seeded pseudorandom generator and simulates 30 days of customer events. Planned scenario shares are rounded to complete episodes. Each row receives `is_fraud = 1{U < p_s}`, with independently generated `U ~ Uniform[0,1)`, conditional on scenario `s`. `p_s` is 0.94 for each fraud scenario, 0.01 for each legitimate edge case, and 0.005 for normal events. Thus labels are noisy, not deterministic. **The previous v3 Bernoulli(sigmoid(z)) label formula is retired and must not be used to interpret v4 results.** Scenario membership itself is not a model feature.

| Scenario | Planned share; episode size | Feature construction | Label probability |
|---|---|---|---:|
| Account takeover | 1.5%; 4 | Existing customer; online electronics, amount 250–2,500, new device, country risk 1–2, distance 250–1,200 km; decline chance .18 | .94 |
| Card testing | 1.5%; 6 | Repeated online electronics 0.5–25, new device, decline chance .70; prior declines/velocity emerge from preceding events | .94 |
| Mule/cash-out | 1.5%; 3 | Existing customer; transfer, category other, amount 1,500–8,000, country risk 1–2, distance 80–700 km | .94 |
| New-account transfer | 1.5%; 2 | New customer, first 14 days; transfer, category other, amount 800–5,000, new device chance .65 | .94 |
| Legitimate travel | 2.5%; 2 | Travel/online, amount 150–1,800, country risk 1–2, distance 300–2,000 km, new device chance .50 | .01 |
| Legitimate large purchase | 2.5%; 1 | Electronics, online or card present, amount 1,800–6,500 | .01 |
| Normal | Remaining rows | Baseline categorical draws and lognormal amount; new device .08; decline chance .03 | .005 |

Base merchant distribution is groceries .32, electronics .13, travel .10, fuel .16, dining .20, other .09; channel distribution card-present .54, online .36, transfer .10. Base amount is lognormal(4.4, 1.08), clipped to 0.01–100,000. Base country-risk levels 0/1/2 have probabilities .82/.14/.04, and distance is exponential(scale=34), clipped to 20,000 km. Customer account age starts at 1–20 days for the new-customer subset and 120–2,200 days otherwise, then increases with simulated days. These are artificial units/proxies, not real currencies, geography or sanctions information.

All events are sorted by simulated time. For each event, `velocity_1h = min(100, number of earlier same-customer events with time > current_time − 3600s)` and `prior_declines_24h = min(100, number of earlier same-customer declined events with time > current_time − 86400s)`. Only **after** these features and label are set is the current event appended to history. A decline is a separately simulated flag, not the fraud label. `customer_id`, `event_time`, `scenario`, `is_declined`, and `is_fraud` are excluded from scoring input. See [data card](DATA_CARD.md) for remaining limitations.
