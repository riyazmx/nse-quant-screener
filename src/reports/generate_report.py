from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


def _safe_len(frame: Any) -> int:
    return 0 if frame is None else int(len(frame))


def _table_as_markdown(frame: Any, columns: list[str], n: int) -> str:
    if frame is None or getattr(frame, "empty", True):
        return "_No data available._\n"

    present = [col for col in columns if col in frame.columns]
    if not present:
        return "_Required columns missing._\n"

    display = frame[present].head(n)
    try:
        return display.to_markdown(index=False) + "\n"
    except Exception:
        return "```\n" + display.to_string(index=False) + "\n```\n"


def generate_markdown_report(
    full_universe: Any,
    cleaned_universe: Any,
    ranked_stocks: Any,
    report_path: Path,
    logger: logging.Logger,
) -> Path:
    """Create the required Phase 3 summary markdown report."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    raw_size = _safe_len(full_universe)
    cleaned_size = _safe_len(cleaned_universe)
    ranked_count = _safe_len(ranked_stocks)

    industries_count = 0
    if cleaned_universe is not None and "industry" in getattr(cleaned_universe, "columns", []):
        industries_count = int(cleaned_universe["industry"].nunique())
    else:
        logger.warning("Missing 'industry' column for industry count.")

    top20 = ranked_stocks
    if ranked_stocks is not None and "total_score" in getattr(ranked_stocks, "columns", []):
        top20 = ranked_stocks.sort_values("total_score", ascending=False).head(20)

    top_industries_section = "_Required columns missing._\n"
    if ranked_stocks is not None and {"industry", "pe_discount"}.issubset(getattr(ranked_stocks, "columns", [])):
        temp = ranked_stocks.sort_values("pe_discount", ascending=False).groupby("industry").head(5)
        counts = temp["industry"].value_counts().head(10).rename_axis("industry").reset_index(name="undervalued_names")
        try:
            top_industries_section = counts.to_markdown(index=False) + "\n"
        except Exception:
            top_industries_section = "```\n" + counts.to_string(index=False) + "\n```\n"
    else:
        logger.warning("Missing columns for top industries undervalued section.")

    value_traps = ranked_stocks
    if ranked_stocks is not None and "category" in getattr(ranked_stocks, "columns", []):
        value_traps = ranked_stocks[ranked_stocks["category"] == "Potential Value Trap"]
    else:
        logger.warning("Missing 'category' for value traps section.")

    quality_notes: list[str] = []
    expected = [
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
        quality_notes.append("Ranked dataset is unavailable.")
    else:
        missing = [col for col in expected if col not in ranked_stocks.columns]
        if missing:
            quality_notes.append("Missing ranked columns: " + ", ".join(missing))

    if not quality_notes:
        quality_notes.append("No major data quality issues detected in required report fields.")

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
            _table_as_markdown(
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
                20,
            ),
            "## Top Industries with Most Undervalued Names",
            top_industries_section,
            "## Top 10 Potential Value Traps",
            _table_as_markdown(
                value_traps,
                ["symbol", "sector", "industry", "pe", "peer_median_pe", "quality_score", "total_score", "category"],
                10,
            ),
            "## Data Quality Notes",
            *[f"- {note}" for note in quality_notes],
            "",
        ]
    )

    report_path.write_text(content, encoding="utf-8")
    return report_path
