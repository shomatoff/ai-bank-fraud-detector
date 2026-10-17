# Synthetic fraud label formula — current v6

For each event `i`, the generator samples an independent `U_i ~ Uniform[0,1)` and sets:

`is_fraud_i = 1{U_i < p(scenario_i)}`.

The four fraud-like scenarios use `p=.88`; legitimate travel and large purchase use `.01`; legitimate many-declines uses `.02`; normal background uses `.01`. For example, a card-testing event with illustrative `U=.20` is labelled 1, while one with `U=.97` is labelled 0. These example draws are **not** claimed to occur in an executed dataset. The 12% negative noise within fraud-like typologies and positive noise elsewhere are author-chosen simulator assumptions, not bank statistics or evidence about a person.

V6 spreads all episodes across the full simulated 30 days; new-account age is measured at the event time. Prior-hour velocity and prior-day declines use only preceding same-customer events. Scenario, synthetic customer ID, event time, decline flag and label are not model inputs. The learned logistic score is a *different* equation, not this generator probability, and its linear contributions are non-causal. With typology label rate `.88`, exact-top-k precision has an *approximate expected* ceiling around `.88` if only fraud-type events are selected; it is not a hard bound in finite samples. See [parameters](SYNTHETIC_SCENARIOS.md), [current evaluation](MODEL_EVALUATION.md) and [archived explanation](archive/SYNTHETIC_FRAUD_LABEL_FORMULA_EN_V4_V5.md).
