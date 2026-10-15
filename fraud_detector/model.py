"""Public training entry point for the synthetic fraud model."""
from __future__ import annotations

import json

from .training import ARTIFACT_DIR, METRICS_PATH, MODEL_PATH, score, train

__all__ = ["ARTIFACT_DIR", "METRICS_PATH", "MODEL_PATH", "score", "train"]


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
