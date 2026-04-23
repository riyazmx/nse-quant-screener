from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from src.utils.config import Config

Row = dict[str, Any]


class PriceLoader:
    """Load placeholder price data for Phase 1 wiring."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[Row]:
        """Return small, deterministic placeholder OHLCV rows."""
        today = date.today()
        return [
            {
                "date": (today - timedelta(days=2)).isoformat(),
                "symbol": "TCS",
                "open": 3600.0,
                "high": 3650.0,
                "low": 3585.0,
                "close": 3625.0,
                "volume": 1200000,
            },
            {
                "date": (today - timedelta(days=1)).isoformat(),
                "symbol": "INFY",
                "open": 1450.0,
                "high": 1472.0,
                "low": 1442.0,
                "close": 1468.0,
                "volume": 980000,
            },
        ]
