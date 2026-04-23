from __future__ import annotations
from typing import Any

from src.utils.config import Config


class PriceLoader:
    """Loads price data for the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[dict[str, Any]]:
        """Return sample price records for Phase 1 scaffolding."""
        return [
            {"symbol": "RELIANCE", "close": 2350.0},
            {"symbol": "TCS", "close": 3200.0},
            {"symbol": "HDFC", "close": 1600.0},
        ]
