"""Conservative delayed-label eligibility for synthetic analyst cases."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

TERMINAL = {"confirmed_fraud", "false_positive"}
PENDING = {"new", "in_review"}


def feedback_summary(rows: list[dict], *, as_of: datetime,
                     maturation_days: int = 7) -> dict:
    """Only terminal statuses older than the embargo are eligible for review.

    Eligibility is not an instruction to retrain. Notes and non-final states are
    never labels, and an updated timestamp is a conservative availability time.
    """
    if as_of.tzinfo is None or not 0 <= maturation_days <= 365:
        raise ValueError("Use timezone-aware as_of and 0..365 maturation days")
    cutoff = as_of.astimezone(UTC) - timedelta(days=maturation_days)
    counts = {"unknown": 0, "pending": 0, "confirmed_fraud": 0, "analyst_false_positive": 0,
              "matured_eligible": 0}
    for row in rows:
        status = row["status"]
        if status in PENDING:
            counts["unknown" if status == "new" else "pending"] += 1
            continue
        if status not in TERMINAL:
            raise ValueError(f"Unknown feedback status: {status}")
        available = datetime.fromisoformat(row["updated_at"])
        created = datetime.fromisoformat(row["created_at"])
        if (available.tzinfo is None or created.tzinfo is None
                or available > as_of or available < created):
            raise ValueError("Feedback timestamps must be ordered and timezone-aware")
        counts["confirmed_fraud" if status == "confirmed_fraud" else "analyst_false_positive"] += 1
        if available <= cutoff:
            counts["matured_eligible"] += 1
    return {
        **counts,
        "as_of_utc": as_of.astimezone(UTC).isoformat(),
        "eligible_before_utc": cutoff.isoformat(),
        "maturation_days": maturation_days,
        "source": "synthetic analyst statuses; not independently verified bank labels",
        "training_automatic": False,
    }
