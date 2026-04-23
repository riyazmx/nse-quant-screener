from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.config import Config


class UniverseFilter:
    """Apply configurable screening filters to the loaded universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def filter(
        self,
        universe: pd.DataFrame | list[dict[str, Any]],
    ) -> pd.DataFrame | list[dict[str, Any]]:
        """Filter the universe using configured sector whitelist."""
        filters = self.config.get("filters", {})
        sector_whitelist = filters.get("sector_whitelist", [])

        if not sector_whitelist:
            return universe

        if isinstance(universe, pd.DataFrame):
            if "sector" not in universe.columns:
                return universe
            return universe.loc[
                universe["sector"].isin(sector_whitelist)
            ].reset_index(drop=True)

        return [
            item
            for item in universe
            if item.get("sector") in sector_whitelist
             ]