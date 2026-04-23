from __future__ import annotations

import numpy as np
import pandas as pd


def _winsorize(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    """Clip extreme values to reduce outlier impact."""
    if series.isna().all():
        return series
    lower_bound = series.quantile(lower)
    upper_bound = series.quantile(upper)
    return series.clip(lower=lower_bound, upper=upper_bound)


def percentile_rank(
    series: pd.Series,
    higher_better: bool = True,
) -> pd.Series:
    """Convert series into percentile rank scores (0–100)."""
    series = pd.to_numeric(series, errors="coerce")

    # Reduce outlier impact
    series = _winsorize(series)

    ranks = series.rank(method="average", pct=True, na_option="keep")

    if not higher_better:
        ranks = 1.0 - ranks

    return ranks * 100.0


def higher_better_score(series: pd.Series) -> pd.Series:
    return percentile_rank(series, higher_better=True)


def lower_better_score(series: pd.Series) -> pd.Series:
    return percentile_rank(series, higher_better=False)