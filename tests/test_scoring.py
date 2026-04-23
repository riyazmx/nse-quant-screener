from __future__ import annotations

import pandas as pd

from src.scoring.categorization import categorize
from src.scoring.score_engine import ScoreEngine


def test_categorization_value_trap() -> None:
    row = pd.Series(
        {
            "value_score": 65.0,
            "quality_score": 45.0,
            "momentum_score": 50.0,
            "risk_penalty": 72.0,
        }
    )

    assert categorize(row) == "Value Trap"


def test_score_engine_produces_ranked_dataframe() -> None:
    technicals = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "1m_return": 2.0,
                "3m_return": 5.0,
                "6m_return": 10.0,
                "12m_return": 20.0,
                "dma_50": 100.0,
                "dma_200": 95.0,
                "volatility": 18.0,
                "max_drawdown": 12.0,
                "atr_pct": 2.0,
                "average_volume_30d": 1_000_000.0,
                "close": 150.0,
            },
            {
                "symbol": "TEST2",
                "1m_return": -1.0,
                "3m_return": 1.0,
                "6m_return": 3.0,
                "12m_return": 8.0,
                "dma_50": 80.0,
                "dma_200": 90.0,
                "volatility": 22.0,
                "max_drawdown": 18.0,
                "atr_pct": 4.0,
                "average_volume_30d": 500_000.0,
                "close": 75.0,
            },
        ]
    )

    fundamentals = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "pe": 15.0,
                "pb": 2.0,
                "roe": 18.0,
                "roce": 20.0,
                "debt_to_equity": 0.6,
                "invalid_pe_flag": False,
            },
            {
                "symbol": "TEST2",
                "pe": 45.0,
                "pb": 5.2,
                "roe": 8.0,
                "roce": 9.0,
                "debt_to_equity": 1.8,
                "invalid_pe_flag": False,
            },
        ]
    )

    peers = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "peer_pe": 18.0,
                "peer_pb": 2.5,
                "peer_roe": 16.0,
                "peer_roce": 17.0,
                "peer_debt_to_equity": 0.8,
                "peer_6m_return": 9.0,
            },
            {
                "symbol": "TEST2",
                "peer_pe": 40.0,
                "peer_pb": 4.5,
                "peer_roe": 11.0,
                "peer_roce": 12.0,
                "peer_debt_to_equity": 1.0,
                "peer_6m_return": 5.0,
            },
        ]
    )

    scored = ScoreEngine(config={}).score(technicals, fundamentals, peers)

    assert "total_score" in scored.columns
    assert all(0.0 <= value <= 100.0 for value in scored["total_score"].fillna(0.0))
    assert scored.loc[scored["symbol"] == "TEST1", "total_score"].iat[0] >= scored.loc[
        scored["symbol"] == "TEST2", "total_score"
    ].iat[0]
