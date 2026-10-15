"""Stable public imports for the time-ordered synthetic training pipeline."""
from __future__ import annotations

from .training_v2 import (
    ARTIFACT_DIR,
    ARTIFACT_VERSION,
    METRICS_PATH,
    MODEL_PATH,
    VALIDATION_PATH,
    choose_threshold,
    explain,
    file_sha256,
    score,
    train,
)

__all__ = [
    "ARTIFACT_DIR", "ARTIFACT_VERSION", "METRICS_PATH", "MODEL_PATH",
    "VALIDATION_PATH", "choose_threshold", "explain", "file_sha256", "score", "train",
]
