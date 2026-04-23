from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.config import Config


class PeerFeatures:
    """Compute peer median statistics for valuation and quality comparisons."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def compute(
        self,
        universe: pd.DataFrame,
        fundamentals: pd.DataFrame,
        technicals: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute peer medians using industry, with sector fallback if industry group is too small."""
        merged = universe.merge(fundamentals, on="symbol", how="left")
        merged = merged.merge(
            technicals[["symbol", "ret_6m"]],
            on="symbol",
            how="left",
        )

        # Fallback: use sector if industry group has fewer than 5 stocks
        industry_counts = merged.groupby("industry")["symbol"].transform("count")
        merged["group_key"] = merged["industry"].where(industry_counts >= 5, merged["sector"])

        # Valid valuation fields
        merged["pe_valid"] = merged["pe"].where(merged["pe"] > 0)
        merged["pb_valid"] = merged["pb"].where(merged["pb"] > 0)

        peer_medians = (
            merged.groupby("group_key")
            .agg(
                peer_median_pe=("pe_valid", "median"),
                peer_median_pb=("pb_valid", "median"),
                peer_median_roe=("roe", "median"),
                peer_median_roce=("roce", "median"),
                peer_median_debt_to_equity=("debt_to_equity", "median"),
                peer_median_ret_6m=("ret_6m", "median"),
            )
            .reset_index()
        )

        merged = merged.merge(peer_medians, on="group_key", how="left")

        # Peer-relative discounts
        valid_pe_discount = (
            merged["pe"].notna()
            & (merged["pe"] > 0)
            & merged["peer_median_pe"].notna()
            & (merged["peer_median_pe"] > 0)
        )
        merged["pe_discount"] = np.where(
            valid_pe_discount,
            (merged["peer_median_pe"] - merged["pe"]) / merged["peer_median_pe"],
            np.nan,
        )

        valid_pb_discount = (
            merged["pb"].notna()
            & (merged["pb"] > 0)
            & merged["peer_median_pb"].notna()
            & (merged["peer_median_pb"] > 0)
        )
        merged["pb_discount"] = np.where(
            valid_pb_discount,
            (merged["peer_median_pb"] - merged["pb"]) / merged["peer_median_pb"],
            np.nan,
        )

        return merged[
            [
                "symbol",
                "peer_median_pe",
                "peer_median_pb",
                "peer_median_roe",
                "peer_median_roce",
                "peer_median_debt_to_equity",
                "peer_median_ret_6m",
                "pe_discount",
                "pb_discount",
            ]
        ]