"""Bounded synthetic review helpers; never authorize a payment decision."""
from __future__ import annotations

import math
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable, Mapping, Sequence


def possible_card_testing_burst(transaction: Mapping) -> bool:
    """Descriptive past-only signal, not an ML score or fraud confirmation."""
    return (
        transaction["amount"] <= 30
        and transaction["channel"] == "online"
        and bool(transaction["is_new_device"])
        and (transaction["velocity_1h"] >= 2 or transaction["prior_declines_24h"] >= 1)
    )


def review_queue(rows: Sequence[Mapping], scores: Sequence[float], capacity: int) -> list[dict]:
    """Return the highest ML scores at an exact bounded batch capacity."""
    if not 1 <= capacity <= 100 or len(rows) != len(scores):
        raise ValueError("Queue requires 1..100 capacity and matching scores")
    if any(not math.isfinite(float(score)) or not 0 <= score <= 1 for score in scores):
        raise ValueError("Queue scores must be finite probabilities")
    ranked = sorted(range(len(rows)), key=lambda index: (-scores[index], index))[:capacity]
    return [
        {
            "id": f"SYN-{index + 1:05d}",
            "probability": round(float(scores[index]), 4),
            "possible_card_testing_burst": possible_card_testing_burst(rows[index]),
        }
        for index in ranked
    ]


class RateLimiter:
    """Small in-memory per-client limit for this single-process loopback demo."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def check(self, key: str, *, limit: int, window_seconds: float = 60) -> int:
        """Return 0 when allowed, else whole seconds to retry (at least one)."""
        if limit < 1 or window_seconds <= 0:
            raise ValueError("Invalid rate limit")
        with self.lock:
            now = self.clock()
            recent = self.events[key]
            while recent and recent[0] <= now - window_seconds:
                recent.popleft()
            if len(recent) >= limit:
                return max(1, math.ceil(recent[0] + window_seconds - now))
            recent.append(now)
            return 0
