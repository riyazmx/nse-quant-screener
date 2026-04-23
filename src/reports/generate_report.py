from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


def _safe_len(frame: Any) -> int:
    if frame is None:
        return 0
    return int(len(frame))


def _format_table(frame: Any, columns: list[str], n: int = 10) -> str:
    if frame is None or getattr(frame, "empty", True):
        return "_No data available._\n"

    present_columns = [c for c in columns if c in frame.columns]
    if not present_columns:
        return "_Required columns missing._\n"

    return frame[present_columns].head(n).to_markdown(index=False) + "\n"


def generate_markdown_report(
    full_universe: Any,
    cleaned_universe: Any,
    ranked_stocks: Any,
    report_path: Path,
    logger: logging.Logger,
) -> Path:
    """Generate Phase 3 markdown summary report."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    raw_size = _safe_len(full_universe)
    cleaned_size = _safe_len(cleaned_universe)
    ranked_count = _safe_len(ranked_stocks)

    industries_count = 0
    if cleaned_universe is not None and "industry" in getattr(cleaned_universe, "columns", []):
        industries_count = int(cleaned_universe["industry"].nunique())
    else:
        logger.warning("Missing 'industry' column for industry count in report.")

    top20 = ranked_stocks.sort_values("total_score", ascending=False) if ranked_stocks is not None and "total_score" in getattr(ranked_stocks, "columns", []) else ranked_stocks

    top_industries_section = "_Required columns missing._\n"
    if ranked_stocks is not None and {"industry", "pe_discount"}.issubset(getattr(ranked_stocks, "columns", [])):
        industry_counts = (
            ranked_stocks.sort_values("pe_discount", ascending=False)
            .groupby("industry")
            .head(5)["industry"]
            .value_counts()
            .head(10)
            .rename_axis("industry")
            .reset_index(name="undervalued_names")
        )
        top_industries_section = industry_counts.to_markdown(index=False) + "\n"
    else:
        logger.warning("Missing columns for top industries undervalued section.")

    value_traps = ranked_stocks
    if ranked_stocks is not None and "category" in getattr(ranked_stocks, "columns", []):
        value_traps = ranked_stocks[ranked_stocks["category"] == "Potential Value Trap"]
    else:
        logger.warning("Missing 'category' column for value trap section.")

    data_quality_notes = []
    expected_columns = [
        "symbol",
        "sector",
        "industry",
        "pe",
        "peer_median_pe",
        "roe",
        "value_score",
        "quality_score",
        "momentum_score",
        "total_score",
        "category",
    ]
    if ranked_stocks is None:
        data_quality_notes.append("Ranked dataset is unavailable.")
    else:
        missing = [c for c in expected_columns if c not in ranked_stocks.columns]
        if missing:
            data_quality_notes.append(f"Missing ranked columns: {', '.join(missing)}")

    if not data_quality_notes:
        data_quality_notes.append("No major data quality issues detected in required report fields.")

    content = "\n".join(
        [
            "# NSE Quant Screener - Phase 3 Summary Report",
            "",
            "## Universe Overview",
            f"- Total raw universe size: **{raw_size}**",
            f"- Cleaned universe size: **{cleaned_size}**",
            f"- Number of industries: **{industries_count}**",
            f"- Number of ranked stocks: **{ranked_count}**",
            "",
            "## Top 20 Ranked Stocks",
            _format_table(
                top20,
                [
                    "symbol",
                    "sector",
                    "industry",
                    "pe",
                    "peer_median_pe",
                    "roe",
                    "value_score",
                    "quality_score",
                    "momentum_score",
                    "total_score",
                    "category",
                ],
                n=20,
            ),
            "## Top Industries with Most Undervalued Names",
            top_industries_section,
            "## Top 10 Potential Value Traps",
            _format_table(
                value_traps,
                ["symbol", "sector", "industry", "pe", "peer_median_pe", "quality_score", "total_score", "category"],
                n=10,
            ),
            "## Data Quality Notes",
            *[f"- {note}" for note in data_quality_notes],
            "",
        ]
    )

    report_path.write_text(content, encoding="utf-8")
    return report_path
