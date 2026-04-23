from __future__ import annotations
from typing import Any

from src.utils.config import Config


class UniverseFilter:
    """Applies screening filters to the loaded universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def filter(self, universe: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter the universe using configured sector whitelist."""
        sector_whitelist = self.config.get("filters", {}).get("sector_whitelist", [])
        if not sector_whitelist:
            return universe

        return [
            item for item in universe if item.get("sector") in sector_whitelist
        ]
