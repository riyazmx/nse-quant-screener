from __future__ import annotations
from typing import Any

from src.utils.config import Config


class MetadataLoader:
    """Loads metadata for stocks in the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[dict[str, Any]]:
        """Return sample metadata records for Phase 1 scaffolding."""
        return [
            {"symbol": "RELIANCE", "exchange": "NSE", "market_cap": 1650000},
            {"symbol": "TCS", "exchange": "NSE", "market_cap": 1370000},
            {"symbol": "HDFC", "exchange": "NSE", "market_cap": 840000},
        ]
