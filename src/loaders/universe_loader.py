from __future__ import annotations
from typing import Any

from src.utils.config import Config


class UniverseLoader:
    """Loads the universe of stocks for screening."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> list[dict[str, Any]]:
        """Return a sample universe listing for Phase 1 scaffolding."""
        return [
            {"symbol": "RELIANCE", "sector": "Energy"},
            {"symbol": "TCS", "sector": "Technology"},
            {"symbol": "HDFC", "sector": "Financial Services"},
        ]
