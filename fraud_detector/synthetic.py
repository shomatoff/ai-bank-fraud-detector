"""Public synthetic generator backed by a chronological customer event stream."""
from __future__ import annotations

from .event_stream import generate_event_stream, generate_transactions

__all__ = ["generate_event_stream", "generate_transactions"]
