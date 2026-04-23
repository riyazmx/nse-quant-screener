from __future__ import annotations

import logging
from pathlib import Path
from typing import Any


def _has_columns(frame: Any, required: list[str]) -> bool:
    if frame is None:
        return False
    frame_columns = set(getattr(frame, "columns", []))
    return set(required).issubset(frame_columns)


def _safe_csv(frame: Any, path: Path, logger: logging.Logger, columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if frame is None:
        logger.warning("Missing dataset for export: %s", path.name)
        path.write_text("", encoding="utf-8")
        return

    output = frame
    if columns is not None:
        missing = [col for col in columns if col not in getattr(frame, "columns", [])]
        if missing:
            logger.warning("Missing columns %s for %s; exporting available columns only.", missing, path.name)
        present = [col for col in columns if col in getattr(frame, "columns", [])]
        if present:
            output = frame[present]

    output.to_csv(path, index=False)


def export_tables(
    full_universe: Any,
    cleaned_universe: Any,
    peer_statistics: Any,
    ranked_stocks: Any,
    tables_dir: Path,
    logger: logging.Logger,
) -> dict[str, Path]:
    """Export Phase 3 CSV tables, warning and continuing on missing columns."""
    tables_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "full_universe": tables_dir / "full_universe.csv",
        "cleaned_universe": tables_dir / "cleaned_universe.csv",
        "peer_statistics": tables_dir / "peer_statistics.csv",
        "ranked_stocks": tables_dir / "ranked_stocks.csv",
        "top_undervalued_by_industry": tables_dir / "top_undervalued_by_industry.csv",
        "top_undervalued_quality": tables_dir / "top_undervalued_quality.csv",
        "value_trap_watchlist": tables_dir / "value_trap_watchlist.csv",
    }

    _safe_csv(full_universe, files["full_universe"], logger)
    _safe_csv(cleaned_universe, files["cleaned_universe"], logger)
    _safe_csv(peer_statistics, files["peer_statistics"], logger)
    _safe_csv(ranked_stocks, files["ranked_stocks"], logger)

    undervalued_by_industry = ranked_stocks
    if _has_columns(ranked_stocks, ["industry", "pe_discount"]):
        undervalued_by_industry = (
            ranked_stocks.sort_values("pe_discount", ascending=False)
            .groupby("industry", as_index=False)
            .head(5)
        )
    else:
        logger.warning("Missing columns for top_undervalued_by_industry; exporting ranked stocks fallback.")
    _safe_csv(undervalued_by_industry, files["top_undervalued_by_industry"], logger)

    undervalued_quality = ranked_stocks
    if _has_columns(ranked_stocks, ["value_score", "quality_score", "total_score"]):
        undervalued_quality = ranked_stocks.sort_values(
            by=["value_score", "quality_score", "total_score"],
            ascending=[False, False, False],
        ).head(25)
    else:
        logger.warning("Missing columns for top_undervalued_quality; exporting ranked stocks fallback.")
    _safe_csv(undervalued_quality, files["top_undervalued_quality"], logger)

    value_traps = ranked_stocks
    if _has_columns(ranked_stocks, ["category"]):
        value_traps = ranked_stocks[ranked_stocks["category"] == "Potential Value Trap"]
        if "total_score" in value_traps.columns:
            value_traps = value_traps.sort_values("total_score", ascending=False)
    else:
        logger.warning("Missing columns for value_trap_watchlist; exporting ranked stocks fallback.")
    _safe_csv(value_traps, files["value_trap_watchlist"], logger)

    return files
