from __future__ import annotations

import pandas as pd

from src.utils.config import Config


class UniverseLoader:
    """Load the NSE stock universe for screening."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        """Return a sample NSE universe with sector and industry metadata."""
        rows = [
            {"symbol": "TCS", "sector": "Technology", "industry": "Enterprise Software", "exchange": "NSE"},
            {"symbol": "INFY", "sector": "Technology", "industry": "Enterprise Software", "exchange": "NSE"},
            {"symbol": "HCLTECH", "sector": "Technology", "industry": "IT Services", "exchange": "NSE"},
            {"symbol": "HDFC", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
            {"symbol": "ICICIBANK", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
            {"symbol": "AXISBANK", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
            {"symbol": "KOTAKBANK", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
            {"symbol": "PNB", "sector": "Financial Services", "industry": "Private Banks", "exchange": "NSE"},
        ]
        return pd.DataFrame(rows)
