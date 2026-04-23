from __future__ import annotations
from typing import Any

from src.utils.config import Config


class FundamentalsLoader:
    """Loads fundamental metrics for the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[dict[str, Any]]:
        """Return sample fundamentals records for Phase 1 scaffolding."""
        return [
            {"symbol": "RELIANCE", "pe": 24.0, "roe": 15.3},
            {"symbol": "TCS", "pe": 29.5, "roe": 37.8},
            {"symbol": "HDFC", "pe": 18.2, "roe": 14.5},
        ]
