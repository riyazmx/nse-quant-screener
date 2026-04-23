from __future__ import annotations

from typing import Any

from src.utils.config import Config

Row = dict[str, Any]


class FundamentalsLoader:
    """Load placeholder fundamentals for Phase 1 wiring."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[Row]:
        """Return sample fundamental records."""
        return [
            {"symbol": "TCS", "pe": 28.0, "pb": 7.0, "roe": 36.0},
            {"symbol": "INFY", "pe": 24.0, "pb": 5.6, "roe": 24.0},
        ]
