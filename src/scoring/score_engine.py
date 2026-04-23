from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from src.scoring.categorization import apply_category
from src.scoring.normalization import higher_better_score, lower_better_score
from src.utils.config import Config


class ScoreEngine:
    """Compute factor scores, penalties, flags, and ranked output."""

    POSITIVE_FACTOR_WEIGHTS: Dict[str, float] = {
        "value_score": 0.30,
        "quality_score": 0.30,
        "momentum_score": 0.25,
        "liquidity_score": 0.15,
    }

    def __init__(self, config: Config) -> None:
        self.config = config

    @staticmethod
    def _weighted_average_from_columns(
        df: pd.DataFrame,
        weights: Dict[str, float],
    ) -> pd.Series:
        """
        Row-wise weighted average with weight renormalization over available values only.
        Returns NaN where no components are available.
        """
        weight_series = pd.Series(weights, dtype=float)
        available = df[list(weights.keys())].notna().astype(float)

        weighted_values = df[list(weights.keys())].mul(weight_series, axis=1)
        numerator = weighted_values.sum(axis=1, skipna=True)
        denominator = available.mul(weight_series, axis=1).sum(axis=1)

        return numerator.div(denominator.replace(0.0, np.nan))

    @staticmethod
    def _combine_growth_components(
        revenue_growth_score: pd.Series,
        earnings_growth_score: pd.Series,
    ) -> pd.Series:
        """Combine growth components using 50/50 weight when both exist."""
        growth_df = pd.DataFrame(
            {
                "revenue_growth_score": revenue_growth_score,
                "earnings_growth_score": earnings_growth_score,
            }
        )
        return ScoreEngine._weighted_average_from_columns(
            growth_df,
            {
                "revenue_growth_score": 0.50,
                "earnings_growth_score": 0.50,
            },
        )

    @staticmethod
    def _safe_log(series: pd.Series) -> pd.Series:
        """Natural log for positive values only; otherwise NaN."""
        return np.log(series.where(series > 0))

    def score(
        self,
        technicals: pd.DataFrame,
        fundamentals: pd.DataFrame,
        peers: pd.DataFrame,
    ) -> pd.DataFrame:
        """Merge inputs, compute all scores, and return ranked DataFrame."""
        df = technicals.merge(fundamentals, on="symbol", how="left")
        df = df.merge(peers, on="symbol", how="left")

        # -----------------------------
        # Core validity flags
        # -----------------------------
        df["invalid_pe_flag"] = df["pe"].isna() | (df["pe"] <= 0)
        df["invalid_pb_flag"] = df["pb"].isna() | (df["pb"] <= 0)

        # -----------------------------
        # Peer-relative metrics
        # -----------------------------
        valid_pe = (~df["invalid_pe_flag"]) & df["peer_median_pe"].notna() & (df["peer_median_pe"] > 0)
        df["pe_discount"] = np.where(
            valid_pe,
            (df["peer_median_pe"] - df["pe"]) / df["peer_median_pe"],
            np.nan,
        )

        valid_pb = (~df["invalid_pb_flag"]) & df["peer_median_pb"].notna() & (df["peer_median_pb"] > 0)
        df["pb_discount"] = np.where(
            valid_pb,
            (df["peer_median_pb"] - df["pb"]) / df["peer_median_pb"],
            np.nan,
        )

        valid_peer_roe = df["roe"].notna() & df["peer_median_roe"].notna()
        roe_den = df["peer_median_roe"].abs().replace(0, 1.0)
        df["roe_rel"] = np.where(
            valid_peer_roe,
            (df["roe"] - df["peer_median_roe"]) / roe_den,
            np.nan,
        )

        valid_peer_roce = df["roce"].notna() & df["peer_median_roce"].notna()
        roce_den = df["peer_median_roce"].abs().replace(0, 1.0)
        df["roce_rel"] = np.where(
            valid_peer_roce,
            (df["roce"] - df["peer_median_roce"]) / roce_den,
            np.nan,
        )

        valid_peer_debt = df["debt_to_equity"].notna() & df["peer_median_debt_to_equity"].notna()
        debt_den = df["peer_median_debt_to_equity"].abs().clip(lower=0.25)
        df["debt_rel_bad"] = np.where(
            valid_peer_debt,
            (df["debt_to_equity"] - df["peer_median_debt_to_equity"]) / debt_den,
            np.nan,
        )

        # -----------------------------
        # Normalized component scores
        # -----------------------------
        df["pe_discount_score"] = higher_better_score(df["pe_discount"])
        df["pb_discount_score"] = higher_better_score(df["pb_discount"])

        df["roe_score"] = higher_better_score(df["roe"])
        df["roce_score"] = higher_better_score(df["roce"])
        df["debt_score"] = lower_better_score(df["debt_to_equity"])
        df["revenue_growth_score"] = higher_better_score(df["revenue_growth"])
        df["earnings_growth_score"] = higher_better_score(df["earnings_growth"])

        # growth component
        df["growth_component"] = self._combine_growth_components(
            df["revenue_growth_score"],
            df["earnings_growth_score"],
        )

        # momentum subcomponents
        df["ret_3m_score"] = higher_better_score(df["ret_3m"])
        df["ret_6m_score"] = higher_better_score(df["ret_6m"])
        df["ret_12m_score"] = higher_better_score(df["ret_12m"])
        df["above_50dma_score"] = df["above_50dma"].fillna(0).astype(float) * 100.0
        df["above_200dma_score"] = df["above_200dma"].fillna(0).astype(float) * 100.0

        # liquidity subcomponents
        df["adv_value_score"] = higher_better_score(self._safe_log(df["adv_60_value"]))
        df["adv_shares_score"] = higher_better_score(self._safe_log(df["adv_60_shares"]))

        # risk subcomponents
        df["vol_penalty_component"] = higher_better_score(df["vol_63"])
        df["mdd_penalty_component"] = higher_better_score(df["mdd_252"].abs())
        df["atr_penalty_component"] = higher_better_score(df["atr_pct"])
        df["weak_trend_penalty_component"] = np.where(
            df["above_200dma"].fillna(0).astype(int) == 0,
            100.0,
            0.0,
        )

        missing_core_fields = [
            "pe",
            "pb",
            "roe",
            "roce",
            "debt_to_equity",
            "revenue_growth",
            "earnings_growth",
            "ret_12m",
        ]
        df["missing_core_count"] = df[missing_core_fields].isna().sum(axis=1)
        df["missing_data_penalty_component"] = (df["missing_core_count"] * 12.5).clip(upper=100.0)

        # -----------------------------
        # Factor scores
        # -----------------------------
        # Value
        df["value_score"] = self._weighted_average_from_columns(
            df,
            {
                "pe_discount_score": 0.60,
                "pb_discount_score": 0.40,
            },
        )

        # Quality
        df["quality_score"] = self._weighted_average_from_columns(
            df,
            {
                "roe_score": 0.30,
                "roce_score": 0.30,
                "debt_score": 0.20,
                "growth_component": 0.20,
            },
        )

        # Momentum
        df["momentum_score"] = self._weighted_average_from_columns(
            df,
            {
                "ret_3m_score": 0.25,
                "ret_6m_score": 0.35,
                "ret_12m_score": 0.20,
                "above_50dma_score": 0.10,
                "above_200dma_score": 0.10,
            },
        )

        # Liquidity
        df["liquidity_score"] = self._weighted_average_from_columns(
            df,
            {
                "adv_value_score": 0.70,
                "adv_shares_score": 0.30,
            },
        )

        # Risk penalty
        df["risk_penalty"] = self._weighted_average_from_columns(
            df,
            {
                "vol_penalty_component": 0.25,
                "mdd_penalty_component": 0.25,
                "atr_penalty_component": 0.20,
                "weak_trend_penalty_component": 0.15,
                "missing_data_penalty_component": 0.15,
            },
        )

        # -----------------------------
        # Final score
        # -----------------------------
        positive_factor_columns = list(self.POSITIVE_FACTOR_WEIGHTS.keys())
        df["positive_factor_count"] = df[positive_factor_columns].notna().sum(axis=1)
        df["insufficient_data_flag"] = df["positive_factor_count"] < 2

        positive_weighted_avg = self._weighted_average_from_columns(
            df,
            self.POSITIVE_FACTOR_WEIGHTS,
        )

        df["total_score"] = positive_weighted_avg - (0.20 * df["risk_penalty"])
        df["total_score"] = df["total_score"].clip(lower=0.0, upper=100.0)

        # -----------------------------
        # Other flags
        # -----------------------------
        df["high_debt_flag"] = df["debt_to_equity"] > 2.0
        df["weak_quality_flag"] = df["quality_score"] < 40.0
        df["weak_momentum_flag"] = df["momentum_score"] < 40.0

        # Illiquid flag should depend on liquidity, not ATR
        df["illiquid_flag"] = (
            df["liquidity_score"].notna()
            & (df["liquidity_score"] < 30.0)
        )

        # -----------------------------
        # Category + ranking
        # -----------------------------
        df = apply_category(df)

        ranked_df = df.loc[~df["insufficient_data_flag"]].copy()
        ranked_df = ranked_df.sort_values(by="total_score", ascending=False).reset_index(drop=True)

        return ranked_df