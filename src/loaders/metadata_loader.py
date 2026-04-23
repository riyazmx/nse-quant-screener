from __future__ import annotations

import pandas as pd

from src.utils.config import Config


class MetadataLoader:
    """Loads metadata for stocks in the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        """Return sample metadata records used for output enrichment."""
        rows = [
            {"symbol": "TCS", "exchange": "NSE", "market_cap": 12_500_000.0},
            {"symbol": "INFY", "exchange": "NSE", "market_cap": 7_200_000.0},
            {"symbol": "HCLTECH", "exchange": "NSE", "market_cap": 4_500_000.0},
            {"symbol": "HDFC", "exchange": "NSE", "market_cap": 5_800_000.0},
            {"symbol": "ICICIBANK", "exchange": "NSE", "market_cap": 3_000_000.0},
            {"symbol": "AXISBANK", "exchange": "NSE", "market_cap": 2_700_000.0},
            {"symbol": "KOTAKBANK", "exchange": "NSE", "market_cap": 3_600_000.0},
            {"symbol": "PNB", "exchange": "NSE", "market_cap": 625_000.0},
        ]
        return pd.DataFrame(rows)
