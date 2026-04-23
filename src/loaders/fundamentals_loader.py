from __future__ import annotations

import pandas as pd

from src.utils.config import Config


class FundamentalsLoader:
    """Load fundamental metrics for the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        """Return sample fundamental ratios for each universe symbol."""
        rows = [
            {
                "symbol": "TCS",
                "pe": 28.0,
                "pb": 7.0,
                "roe": 36.0,
                "roce": 38.0,
                "debt_to_equity": 0.2,
                "revenue_growth": 12.0,
                "earnings_growth": 14.0,
            },
            {
                "symbol": "INFY",
                "pe": 24.0,
                "pb": 5.6,
                "roe": 24.0,
                "roce": 26.0,
                "debt_to_equity": 0.1,
                "revenue_growth": 10.0,
                "earnings_growth": 11.0,
            },
            {
                "symbol": "HCLTECH",
                "pe": 18.0,
                "pb": 3.4,
                "roe": 20.0,
                "roce": 21.0,
                "debt_to_equity": 0.3,
                "revenue_growth": 9.0,
                "earnings_growth": 10.5,
            },
            {
                "symbol": "HDFC",
                "pe": 18.5,
                "pb": 3.8,
                "roe": 17.0,
                "roce": 18.5,
                "debt_to_equity": 0.9,
                "revenue_growth": 8.0,
                "earnings_growth": 9.0,
            },
            {
                "symbol": "ICICIBANK",
                "pe": 12.0,
                "pb": 1.8,
                "roe": 13.0,
                "roce": 14.0,
                "debt_to_equity": 2.1,
                "revenue_growth": 6.0,
                "earnings_growth": 5.0,
            },
            {
                "symbol": "AXISBANK",
                "pe": 15.0,
                "pb": 1.9,
                "roe": 15.5,
                "roce": 16.0,
                "debt_to_equity": 1.8,
                "revenue_growth": 7.0,
                "earnings_growth": 7.5,
            },
            {
                "symbol": "KOTAKBANK",
                "pe": 20.0,
                "pb": 2.8,
                "roe": 18.0,
                "roce": 19.0,
                "debt_to_equity": 1.2,
                "revenue_growth": 8.5,
                "earnings_growth": 9.5,
            },
            {
                "symbol": "PNB",
                "pe": 9.5,
                "pb": 0.9,
                "roe": 8.0,
                "roce": 9.0,
                "debt_to_equity": 3.5,
                "revenue_growth": 2.0,
                "earnings_growth": 1.0,
            },
        ]
        return pd.DataFrame(rows)
