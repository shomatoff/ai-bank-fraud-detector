# Current v6 synthetic scenarios — simulation assumptions, not bank facts

All planned episodes are stratified with random jitter across the **whole 30-day simulated window**. Episode counts are rounded to whole episodes. The new-account opening is set shortly before its own event, so an event in late validation can still have a young account. This corrects the v5 early-time bias. Exact code: `fraud_detector/event_stream.py`; older parameter tables are [archived](archive/SYNTHETIC_SCENARIOS_V4_V5.md).

| Scenario | Planned share; episode size | Artificial feature pattern | Positive-label probability |
|---|---|---|---:|
| Account takeover | 1.5%; 4 | Existing account, online electronics, amount 250–2,500, new device, country-risk 1–2, distance 250–1,200 km | .88 |
| Card testing | 1.5%; 6 | Online electronics amount .5–25, new device, decline probability .70, past-only burst counts | .88 |
| Mule/cash-out | 1.5%; 3 | Existing account, transfer/other, amount 1,500–8,000, country-risk 1–2, distance 80–700 km | .88 |
| New-account transfer | 1.5%; 2 | Account opened 1–14 days before event, transfer/other, amount 800–5,000, new-device chance .65 | .88 |
| Legitimate travel | 2.5%; 2 | Travel/online, amount 150–1,800, country-risk 1–2, distance 300–2,000 km, new-device chance .50 | .01 |
| Legitimate large purchase | 2.5%; 1 | Electronics, online or card-present, amount 1,800–6,500 | .01 |
| Legitimate many declines | 2.5%; 5 | Online electronics, amount 100–1,800, new-device chance .50, country-risk mix .2/.6/.2, decline chance .85 | .02 |
| Normal | Remainder | Baseline categorical and lognormal draws, new-device chance .08, decline chance .03 | .01 |

For each event `i`, independently draw `U_i ~ Uniform[0,1)` and set `is_fraud_i = 1{U_i < p(scenario_i)}`. The label has deliberate noise and does **not** assert real wrongdoing. Customer, scenario and label are excluded from model inputs. `velocity_1h` and `prior_declines_24h` use only preceding same-customer events. [EN formula](SYNTHETIC_FRAUD_LABEL_FORMULA_EN.md) · [UZ](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md) · [RU](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md) · [evaluation](MODEL_EVALUATION.md).
