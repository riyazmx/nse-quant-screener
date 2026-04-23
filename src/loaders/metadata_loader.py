from __future__ import annotations

from typing import Any

from src.utils.config import Config

Row = dict[str, Any]


class MetadataLoader:
    """Load placeholder metadata for Phase 1 wiring."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[Row]:
        """Return sample stock metadata."""
        return [
            {"symbol": "TCS", "exchange": "NSE", "market_cap": 12500000.0},
            {"symbol": "INFY", "exchange": "NSE", "market_cap": 7200000.0},
        ]
