from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.config import Config


class PriceLoader:
    """Load synthetic but realistic sample price data for the universe."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self) -> pd.DataFrame:
        """Return deterministic sample OHLCV series suitable for feature engineering."""
        end_date = pd.Timestamp.now().normalize()
        dates = pd.bdate_range(end=end_date, periods=260)

        templates = {
            "TCS": {"base_price": 3000.0, "avg_volume": 1_500_000.0, "annual_drift": 0.14, "annual_vol": 0.22},
            "INFY": {"base_price": 1600.0, "avg_volume": 1_200_000.0, "annual_drift": 0.12, "annual_vol": 0.24},
            "HCLTECH": {"base_price": 1200.0, "avg_volume": 900_000.0, "annual_drift": 0.10, "annual_vol": 0.23},
            "HDFC": {"base_price": 1600.0, "avg_volume": 2_000_000.0, "annual_drift": 0.11, "annual_vol": 0.20},
            "ICICIBANK": {"base_price": 720.0, "avg_volume": 2_200_000.0, "annual_drift": 0.15, "annual_vol": 0.28},
            "AXISBANK": {"base_price": 870.0, "avg_volume": 1_800_000.0, "annual_drift": 0.13, "annual_vol": 0.27},
            "KOTAKBANK": {"base_price": 1950.0, "avg_volume": 1_100_000.0, "annual_drift": 0.09, "annual_vol": 0.21},
            "PNB": {"base_price": 70.0, "avg_volume": 4_500_000.0, "annual_drift": 0.08, "annual_vol": 0.35},
        }

        rng = np.random.default_rng(42)
        records: list[dict[str, float | str | pd.Timestamp]] = []

        n = len(dates)
        t = np.arange(n)

        for symbol, template in templates.items():
            base_price = template["base_price"]
            avg_volume = template["avg_volume"]
            annual_drift = template["annual_drift"]
            annual_vol = template["annual_vol"]

            daily_drift = annual_drift / 252.0
            daily_vol = annual_vol / np.sqrt(252.0)

            # Mild deterministic seasonality + small random noise
            seasonal = 0.0003 * np.sin(2 * np.pi * t / 63.0)
            shocks = rng.normal(loc=0.0, scale=daily_vol, size=n)

            log_returns = daily_drift + seasonal + shocks
            log_price = np.log(base_price) + np.cumsum(log_returns)
            close = np.exp(log_price)

            # Build OHLC around close
            prev_close = np.r_[close[0], close[:-1]]
            open_price = prev_close * (1.0 + rng.normal(0.0, 0.002, size=n))

            intraday_spread = np.maximum(0.003, np.abs(rng.normal(0.008, 0.003, size=n)))
            high = np.maximum(open_price, close) * (1.0 + intraday_spread)
            low = np.minimum(open_price, close) * (1.0 - intraday_spread)

            # Realistic varying volume
            volume_wave = 1.0 + 0.10 * np.sin(2 * np.pi * t / 42.0)
            volume_noise = rng.normal(1.0, 0.05, size=n)
            volume = np.maximum(1.0, avg_volume * volume_wave * volume_noise)

            for i, date in enumerate(dates):
                records.append(
                    {
                        "date": date,
                        "symbol": symbol,
                        "open": float(open_price[i]),
                        "high": float(high[i]),
                        "low": float(low[i]),
                        "close": float(close[i]),
                        "volume": float(volume[i]),
                    }
                )

        return pd.DataFrame(records)