from __future__ import annotations

import pandas as pd

from src.utils.config import Config


class FundamentalFeatures:
    """Normalizes and validates fundamental ratios."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def compute(self, fundamentals: pd.DataFrame) -> pd.DataFrame:
        fundamentals = fundamentals.copy()
        numeric_columns = [
            "pe",
            "pb",
            "roe",
            "roce",
            "debt_to_equity",
            "revenue_growth",
            "earnings_growth",
        ]

        for column in numeric_columns:
            fundamentals[column] = pd.to_numeric(fundamentals[column], errors="coerce")

        fundamentals["invalid_pe_flag"] = (fundamentals["pe"] <= 0) | fundamentals["pe"].isna()
        fundamentals["invalid_pb_flag"] = (fundamentals["pb"] <= 0) | fundamentals["pb"].isna()
        return fundamentals
