from __future__ import annotations

import pandas as pd

from src.scoring.score_engine import ScoreEngine


def test_score_engine_produces_ranked_dataframe() -> None:
    technicals = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "close": 150.0,
                "ret_3m": 0.08,
                "ret_6m": 0.14,
                "ret_12m": 0.24,
                "above_50dma": 1.0,
                "above_200dma": 1.0,
                "vol_63": 0.18,
                "mdd_252": -0.12,
                "atr_pct": 0.02,
                "adv_60_value": 150_000_000.0,
                "adv_60_shares": 1_000_000.0,
            },
            {
                "symbol": "TEST2",
                "close": 75.0,
                "ret_3m": 0.01,
                "ret_6m": 0.03,
                "ret_12m": 0.08,
                "above_50dma": 0.0,
                "above_200dma": 0.0,
                "vol_63": 0.30,
                "mdd_252": -0.25,
                "atr_pct": 0.05,
                "adv_60_value": 20_000_000.0,
                "adv_60_shares": 300_000.0,
            },
        ]
    )

    fundamentals = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "pe": 14.0,
                "pb": 1.9,
                "roe": 19.0,
                "roce": 20.0,
                "debt_to_equity": 0.5,
                "revenue_growth": 11.0,
                "earnings_growth": 12.0,
            },
            {
                "symbol": "TEST2",
                "pe": 40.0,
                "pb": 5.0,
                "roe": 8.0,
                "roce": 9.0,
                "debt_to_equity": 2.2,
                "revenue_growth": 3.0,
                "earnings_growth": 2.0,
            },
        ]
    )

    peers = pd.DataFrame(
        [
            {
                "symbol": "TEST1",
                "peer_median_pe": 18.0,
                "peer_median_pb": 2.5,
                "peer_median_roe": 15.0,
                "peer_median_roce": 16.0,
                "peer_median_debt_to_equity": 0.8,
                "peer_median_ret_6m": 0.10,
                "pe_discount": (18.0 - 14.0) / 18.0,
                "pb_discount": (2.5 - 1.9) / 2.5,
            },
            {
                "symbol": "TEST2",
                "peer_median_pe": 30.0,
                "peer_median_pb": 3.5,
                "peer_median_roe": 12.0,
                "peer_median_roce": 13.0,
                "peer_median_debt_to_equity": 1.4,
                "peer_median_ret_6m": 0.06,
                "pe_discount": (30.0 - 40.0) / 30.0,
                "pb_discount": (3.5 - 5.0) / 3.5,
            },
        ]
    )

    scored = ScoreEngine(config={}).score(technicals, fundamentals, peers)

    assert "total_score" in scored.columns
    assert "category" in scored.columns
    assert scored["total_score"].between(0.0, 100.0).all()
    assert scored.iloc[0]["symbol"] == "TEST1"
