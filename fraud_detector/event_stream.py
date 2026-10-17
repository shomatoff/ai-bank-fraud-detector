"""Synthetic customer event stream with past-only rolling features.

Customer IDs are internal synthetic grouping keys, never model inputs.
Scenario membership creates noisy labels; it is never an input feature.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from .features import CATEGORIES, CHANNELS, FEATURES

SCENARIOS = {
    "account_takeover": {"share": 0.015, "episode": 4, "positive_rate": 0.88},
    "card_testing": {"share": 0.015, "episode": 6, "positive_rate": 0.88},
    "mule_cashout": {"share": 0.015, "episode": 3, "positive_rate": 0.88},
    "new_account_transfer": {"share": 0.015, "episode": 2, "positive_rate": 0.88},
    "legit_travel": {"share": 0.025, "episode": 2, "positive_rate": 0.01},
    "legit_large_purchase": {"share": 0.025, "episode": 1, "positive_rate": 0.01},
    "legit_many_declines": {"share": 0.025, "episode": 5, "positive_rate": 0.02},
}
NORMAL_POSITIVE_RATE = 0.01
WINDOW_SECONDS = 30 * 24 * 3600


def generate_event_stream(
    count: int = 12000, seed: int = 42, start: str = "2026-01-01"
) -> pd.DataFrame:
    """Return chronological synthetic events and labels.

    velocity_1h counts previous events from the same customer in the prior hour.
    prior_declines_24h counts previous declined events in the prior day.
    The current event and all later events are excluded from both windows.
    """
    if count < 100:
        raise ValueError("At least 100 rows are required")
    rng = np.random.default_rng(seed)
    new_episodes = int(np.ceil(max(2, round(count * SCENARIOS["new_account_transfer"]["share"])) / 2))
    customer_count = max(40 + new_episodes, count // 20)
    ages = rng.integers(120, 2200, customer_count)
    old_customers = np.arange(new_episodes, customer_count)
    opened_at = np.full(customer_count, -1, dtype=int)

    plans: list[tuple[int, int, str]] = []
    for scenario, config in SCENARIOS.items():
        target = max(config["episode"], round(count * config["share"]))
        episode_count = int(np.ceil(target / config["episode"]))
        for episode_index, offset in enumerate(range(0, target, config["episode"])):
            # Stratification plus within-stratum jitter spreads each type through
            # the entire month without using labels or later events as features.
            anchor = int((episode_index + rng.random()) / episode_count * (WINDOW_SECONDS - 3600))
            if scenario == "new_account_transfer":
                customer = episode_index
                # The account opens shortly before its own event, including in
                # late calibration/validation windows, not at simulation start.
                opened_at[customer] = anchor - int(rng.integers(1, 15) * 86400)
            else:
                customer = int(rng.choice(old_customers))
            for step in range(min(config["episode"], target - offset)):
                # Explicit preceding activity makes card testing and cash-out bursts.
                plans.append((anchor + step * int(rng.integers(60, 240)), customer, scenario))
    if len(plans) > count:
        plans = plans[:count]
    for _ in range(count - len(plans)):
        seconds = int(rng.integers(0, WINDOW_SECONDS))
        customer = int(rng.integers(0, customer_count))
        if opened_at[customer] > seconds:
            customer = int(rng.choice(old_customers))
        plans.append((
            seconds,
            customer,
            "normal",
        ))
    plans.sort(key=lambda item: item[0])

    base = datetime.fromisoformat(start).replace(tzinfo=UTC)
    histories: dict[int, deque[int]] = defaultdict(deque)
    declines: dict[int, deque[int]] = defaultdict(deque)
    rows: list[dict] = []
    for seconds, customer, scenario in plans:
        recent = histories[customer]
        prior_bad = declines[customer]
        while recent and recent[0] <= seconds - 3600:
            recent.popleft()
        while prior_bad and prior_bad[0] <= seconds - 86400:
            prior_bad.popleft()
        velocity = min(len(recent), 100)
        prior_declines = min(len(prior_bad), 100)
        age = int(min(36500, max(1, (seconds - opened_at[customer]) // 86400)
                      if opened_at[customer] != -1 else ages[customer] + seconds // 86400))
        category = str(rng.choice(CATEGORIES, p=[.32, .13, .10, .16, .20, .09]))
        channel = str(rng.choice(CHANNELS, p=[.54, .36, .10]))
        amount = float(np.clip(rng.lognormal(4.4, 1.08), .01, 100000))
        country_risk = int(rng.choice([0, 1, 2], p=[.82, .14, .04]))
        new_device = bool(rng.random() < .08)
        distance = float(np.clip(rng.exponential(34), 0, 20000))
        decline_probability = 0.03
        if scenario == "account_takeover":
            category, channel = "electronics", "online"
            amount = float(rng.uniform(250, 2500))
            country_risk, new_device = int(rng.choice([1, 2])), True
            distance, decline_probability = float(rng.uniform(250, 1200)), 0.18
        elif scenario == "card_testing":
            category, channel = "electronics", "online"
            amount = float(rng.uniform(.5, 25))
            new_device, decline_probability = True, 0.70
        elif scenario == "mule_cashout":
            category, channel = "other", "transfer"
            amount = float(rng.uniform(1500, 8000))
            country_risk = int(rng.choice([1, 2]))
            distance = float(rng.uniform(80, 700))
        elif scenario == "new_account_transfer":
            category, channel = "other", "transfer"
            amount = float(rng.uniform(800, 5000))
            new_device = bool(rng.random() < .65)
        elif scenario == "legit_travel":
            category, channel = "travel", "online"
            amount = float(rng.uniform(150, 1800))
            country_risk = int(rng.choice([1, 2]))
            new_device = bool(rng.random() < .50)
            distance = float(rng.uniform(300, 2000))
        elif scenario == "legit_large_purchase":
            category = "electronics"
            channel = str(rng.choice(["online", "card_present"]))
            amount = float(rng.uniform(1800, 6500))
        elif scenario == "legit_many_declines":
            category, channel = "electronics", "online"
            amount = float(rng.uniform(100, 1800))
            new_device = bool(rng.random() < .50)
            country_risk = int(rng.choice([0, 1, 2], p=[.2, .6, .2]))
            decline_probability = 0.85
        declined = bool(rng.random() < decline_probability)
        positive_rate = SCENARIOS[scenario]["positive_rate"] if scenario in SCENARIOS else NORMAL_POSITIVE_RATE
        row = {
            "customer_id": f"SYN-C{customer:05d}",
            "event_time": base + timedelta(seconds=seconds),
            "scenario": scenario,
            "amount": round(amount, 2),
            "hour": (base + timedelta(seconds=seconds)).hour,
            "merchant_category": category,
            "channel": channel,
            "country_risk": country_risk,
            "is_new_device": new_device,
            "velocity_1h": velocity,
            "distance_km": round(distance, 1),
            "account_age_days": age,
            "prior_declines_24h": prior_declines,
            "is_declined": declined,
            "is_fraud": int(rng.random() < positive_rate),
        }
        rows.append(row)
        # Update histories only after features and label have been assigned.
        recent.append(seconds)
        if declined:
            prior_bad.append(seconds)
    result = pd.DataFrame(rows)
    assert len(result) == count
    assert result.event_time.is_monotonic_increasing
    assert set(FEATURES) <= set(result.columns)
    return result


def generate_transactions(count: int = 12000, seed: int = 42) -> pd.DataFrame:
    """Backward-compatible public table: only model features and artificial label."""
    return generate_event_stream(count, seed)[FEATURES + ["is_fraud"]].copy()
