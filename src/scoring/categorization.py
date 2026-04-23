from __future__ import annotations

import pandas as pd


def categorize(row: pd.Series) -> str:
    """Assign exactly one category using first-match logic."""
    value_score = row.get("value_score", float("nan"))
    quality_score = row.get("quality_score", float("nan"))
    momentum_score = row.get("momentum_score", float("nan"))
    illiquid_flag = bool(row.get("illiquid_flag", False))
    cyclical_tag = bool(row.get("cyclical_tag", False))

    # 1. Illiquid / Avoid
    if illiquid_flag:
        return "Illiquid / Avoid"

    # 2. Potential Value Trap
    if pd.notna(value_score) and pd.notna(quality_score):
        if value_score >= 60 and quality_score < 40:
            return "Potential Value Trap"

    # 3. Undervalued but Weak Quality
    if pd.notna(value_score) and pd.notna(quality_score):
        if value_score >= 60 and 40 <= quality_score < 55:
            return "Undervalued but Weak Quality"

    # 4. Undervalued Quality
    if pd.notna(value_score) and pd.notna(quality_score) and pd.notna(momentum_score):
        if value_score >= 60 and quality_score >= 55 and momentum_score >= 45:
            return "Undervalued Quality"

    # 5. Expensive Momentum Leader
    if pd.notna(value_score) and pd.notna(quality_score) and pd.notna(momentum_score):
        if value_score < 40 and quality_score >= 60 and momentum_score >= 70:
            return "Expensive Momentum Leader"

    # 6. Fairly Valued Leader
    if pd.notna(value_score) and pd.notna(quality_score) and pd.notna(momentum_score):
        if 40 <= value_score < 60 and quality_score >= 60 and momentum_score >= 60:
            return "Fairly Valued Leader"

    # 7. Cyclical Value
    if cyclical_tag and pd.notna(value_score):
        if value_score >= 55:
            return "Cyclical Value"

    # 8. Neutral
    return "Neutral"


def apply_category(df: pd.DataFrame) -> pd.DataFrame:
    """Apply categorization row-wise."""
    result = df.copy()
    result["category"] = result.apply(categorize, axis=1)
    return result