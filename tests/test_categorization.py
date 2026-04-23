from __future__ import annotations

import pandas as pd

from src.scoring.categorization import categorize


def test_categorization_potential_value_trap() -> None:
    row = pd.Series(
        {
            "value_score": 65.0,
            "quality_score": 35.0,
            "momentum_score": 50.0,
            "illiquid_flag": False,
            "cyclical_tag": False,
        }
    )

    assert categorize(row) == "Potential Value Trap"


def test_categorization_illiquid_first_match() -> None:
    row = pd.Series(
        {
            "value_score": 80.0,
            "quality_score": 90.0,
            "momentum_score": 90.0,
            "illiquid_flag": True,
        }
    )

    assert categorize(row) == "Illiquid / Avoid"
