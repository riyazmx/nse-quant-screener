from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.config import Config


class TechnicalFeatures:
    """Compute technical indicators used for scoring."""

    def __init__(self, config: Config) -> None:
        self.config = config

    @staticmethod
    def _price_return(series: pd.Series, periods: int) -> float:
        """Return price change over lookback window in decimal form."""
        if len(series) < periods + 1:
            return np.nan
        start_price = series.iloc[-periods - 1]
        end_price = series.iloc[-1]
        if pd.isna(start_price) or start_price == 0:
            return np.nan
        return float((end_price / start_price) - 1.0)

    @staticmethod
    def _annualized_volatility(series: pd.Series, window: int = 63) -> float:
        """Compute annualized volatility from daily returns in decimal form."""
        returns = series.pct_change().dropna()
        if len(returns) >= window:
            returns = returns.iloc[-window:]
        if returns.empty:
            return np.nan
        return float(returns.std(ddof=0) * np.sqrt(252))

    @staticmethod
    def _max_drawdown(series: pd.Series, window: int = 252) -> float:
        """Compute max drawdown over lookback window in decimal form (negative value)."""
        if len(series) < 2:
            return np.nan
        lookback = series.iloc[-window:]
        rolling_peak = lookback.cummax()
        drawdown = (lookback / rolling_peak) - 1.0
        return float(drawdown.min())

    @staticmethod
    def _atr_pct(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        window: int = 14,
    ) -> float:
        """Compute ATR as a fraction of latest close."""
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window, min_periods=window).mean().iloc[-1]

        latest_close = close.iloc[-1]
        if pd.isna(atr) or pd.isna(latest_close) or latest_close == 0:
            return np.nan

        return float(atr / latest_close)

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Compute technical features per symbol."""
        rows: list[dict[str, float | str]] = []

        for symbol, group in prices.groupby("symbol"):
            series = group.sort_values("date").reset_index(drop=True)

            close = series["close"]
            high = series["high"]
            low = series["low"]
            volume = series["volume"]

            dma_50 = close.rolling(50, min_periods=50).mean().iloc[-1]
            dma_200 = close.rolling(200, min_periods=200).mean().iloc[-1]

            adv_60_shares = volume.rolling(60, min_periods=60).mean().iloc[-1]
            adv_60_value = (close * volume).rolling(60, min_periods=60).mean().iloc[-1]

            latest_close = close.iloc[-1]

            rows.append(
                {
                    "symbol": symbol,
                    "close": float(latest_close),
                    "ret_3m": self._price_return(close, 63),
                    "ret_6m": self._price_return(close, 126),
                    "ret_12m": self._price_return(close, 252),
                    "above_50dma": float(pd.notna(dma_50) and latest_close > dma_50),
                    "above_200dma": float(pd.notna(dma_200) and latest_close > dma_200),
                    "vol_63": self._annualized_volatility(close, window=63),
                    "mdd_252": self._max_drawdown(close, window=252),
                    "atr_pct": self._atr_pct(high, low, close, window=14),
                    "adv_60_value": float(adv_60_value) if pd.notna(adv_60_value) else np.nan,
                    "adv_60_shares": float(adv_60_shares) if pd.notna(adv_60_shares) else np.nan,
                    "dma_50": float(dma_50) if pd.notna(dma_50) else np.nan,
                    "dma_200": float(dma_200) if pd.notna(dma_200) else np.nan,
                }
            )

        return pd.DataFrame(rows)