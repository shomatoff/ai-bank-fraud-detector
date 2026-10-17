# Dataset and limitations

The application uses generated data only. `generate_event_stream(count=12000, seed=42)` creates a chronological 30-day synthetic event stream; `generate_transactions` exposes the model features plus the artificial `is_fraud` label. The generator has seven named scenarios, noisy positive rates, ordinary events, and past-only `velocity_1h` and `prior_declines_24h` windows. Scenario, synthetic customer ID, event time, decline flag and label are withheld from model features.

The model feature contract is in `fraud_detector/features.py`: amount, hour, merchant category, channel, country risk, new-device flag, one-hour velocity, distance, account age and prior declines. The training pipeline uses a 60% fit / 20% calibration / 20% validation chronological development split and a later test seed. The validation split selects the model and alert threshold; the later test is not used for tuning.

These are simulator labels coupled to simulator patterns. They do not establish fraud, fairness, calibration, operational performance, or real-bank generalisation. The held-out `card_testing` result is particularly weak in the current multi-seed audit. The optional ULB-shaped benchmark loader has only been exercised with a tiny synthetic fixture; no public ULB CSV or customer data is committed.

Do not put PAN, CVV, PIN, passwords, access tokens, names, addresses or real transaction records into this application. See [MODEL_EVALUATION](MODEL_EVALUATION.md) and [MODEL_CARD](MODEL_CARD.md) for measured synthetic results and caveats.
