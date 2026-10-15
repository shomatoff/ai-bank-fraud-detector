# Synthetic fraud label formula — English (v4)

This formula **creates a simulation label**, not evidence that a person committed fraud. The v3 `Bernoulli(sigmoid(z))` equation is historical and is **not used** in v4. Related: [O‘zbek](SYNTHETIC_FRAUD_LABEL_FORMULA_UZ.md), [Русский](SYNTHETIC_FRAUD_LABEL_FORMULA_RU.md), [scenarios](SYNTHETIC_SCENARIOS.md), [evaluation](MODEL_EVALUATION.md), [capability audit](FRAUD_DETECTION_CAPABILITIES.md).

First, `generate_event_stream(count, seed, start)` assigns each planned episode one of seven scenario names. Fraud-like scenarios (`account_takeover`, `card_testing`, `mule_cashout`, `new_account_transfer`) each target 1.5% of rows. Legitimate travel and large-purchase cases each target 2.5%; the remainder is `normal`. Rounding to complete episodes means exact counts can differ from planned percentages. Each scenario sets synthetic feature ranges: e.g. card testing yields several small online charges and many simulated declines; legitimate travel can also have a new device, a long distance and high country-risk level. See the exact parameter table in [scenarios](SYNTHETIC_SCENARIOS.md).

For each row `i`, the generator samples a fresh pseudorandom number `U_i ~ Uniform[0,1)` and sets

`is_fraud_i = 1 if U_i < p(scenario_i), otherwise 0`, where

`p(account_takeover)=p(card_testing)=p(mule_cashout)=p(new_account_transfer)=0.94`, `p(legit_travel)=p(legit_large_purchase)=0.01`, and `p(normal)=0.005`.

Example 1: a card-testing event with `U=.20` receives label 1 because `.20 < .94`; another card-testing event with `U=.97` receives label 0 despite the same typology. Example 2: a genuine-travel scenario with `U=.50` receives 0 because `.50 ≥ .01`, whereas `U=.005` receives noisy label 1. These examples illustrate the rule; they are **not** claims that those exact draws occurred in the executed dataset. In the actual seeded run, the generated prevalence is measured, not set by this equation alone.

`velocity_1h` counts earlier events of the same synthetic customer within 3600 seconds; `prior_declines_24h` counts earlier separately simulated declines within 86400 seconds. Current/future events and the fraud label never enter either count. Scenario name and customer ID are withheld from the model. The model fits a **different** logistic equation from ten observable synthetic features and then a Platt sigmoid on disjoint data; its predicted probability is not the generator’s `p(scenario)` and not a real-bank fraud probability. Its top linear terms explain its score mathematically, not fraud causally. Human trust should rest on provenance, held-out errors, review and limitations—not on treating a simulator label as real ground truth.
