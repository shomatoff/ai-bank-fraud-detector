from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CATEGORIES = ("groceries", "electronics", "travel", "fuel", "dining", "other")
CHANNELS = ("card_present", "online", "transfer")
FEATURES = [
    "amount", "hour", "merchant_category", "channel", "country_risk",
    "is_new_device", "velocity_1h", "distance_km", "account_age_days",
    "prior_declines_24h",
]


class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(ge=0.01, le=100000)
    hour: int = Field(ge=0, le=23)
    merchant_category: Literal["groceries", "electronics", "travel", "fuel", "dining", "other"]
    channel: Literal["card_present", "online", "transfer"]
    country_risk: int = Field(ge=0, le=2)
    is_new_device: bool
    velocity_1h: int = Field(ge=0, le=100)
    distance_km: float = Field(ge=0, le=20000)
    account_age_days: int = Field(ge=0, le=36500)
    prior_declines_24h: int = Field(ge=0, le=100)
