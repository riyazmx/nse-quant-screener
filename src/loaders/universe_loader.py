from __future__ import annotations

from typing import Any

from src.utils.config import Config

Row = dict[str, Any]


class UniverseLoader:
    """Load the stock universe for screening."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[Row]:
        """Return a small placeholder universe dataset."""
        return [
            {"symbol": "TCS", "sector": "Technology", "industry": "Enterprise Software", "exchange": "NSE"},
            {"symbol": "INFY", "sector": "Technology", "industry": "Enterprise Software", "exchange": "NSE"},
            {"symbol": "HDFCBANK", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
        ]
