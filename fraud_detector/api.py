"""Stable FastAPI entry point for the synthetic-only local application."""
from __future__ import annotations

from .api_v2 import app, connect, create_app

__all__ = ["app", "connect", "create_app"]
