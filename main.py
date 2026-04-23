from __future__ import annotations

from pathlib import Path
from typing import Any

from src.reports import export_tables, generate_charts, generate_markdown_report
from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger


def _safe_len(frame: Any) -> int:
    return 0 if frame is None else int(len(frame))


def _print_console_summary(full_universe: Any, cleaned_universe: Any, ranked_stocks: Any, logger) -> None:
    """Print Phase 3 console summary with graceful handling for missing fields."""
    raw_size = _safe_len(full_universe)
    cleaned_size = _safe_len(cleaned_universe)
    ranked_count = _safe_len(ranked_stocks)

    industries_count = 0
    if cleaned_universe is not None and "industry" in getattr(cleaned_universe, "columns", []):
        industries_count = int(cleaned_universe["industry"].nunique())
    else:
        logger.warning("Missing 'industry' for console summary industry count.")

    print("\n=== Phase 3 Console Summary ===")
    print(f"Raw universe size: {raw_size}")
    print(f"Cleaned universe size: {cleaned_size}")
    print(f"Number of industries: {industries_count}")
    print(f"Ranked stocks count: {ranked_count}")

    required_cols = [
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

    if ranked_stocks is None or getattr(ranked_stocks, "empty", True):
        print("Top 10 ranked stocks: no data available")
        return

    present = [c for c in required_cols if c in ranked_stocks.columns]
    missing = [c for c in required_cols if c not in ranked_stocks.columns]
    if missing:
        logger.warning("Missing columns in console top-10 output: %s", missing)

    top10 = ranked_stocks.sort_values("total_score", ascending=False).head(10)
    print("\nTop 10 ranked stocks:")
    print(top10[present].to_string(index=False))


def main() -> None:
    """Run Phase 3 pipeline: scoring, exports, charts, markdown report, and console summary."""
    project_root = Path(__file__).resolve().parent
    config = ConfigLoader.load(project_root / "config" / "settings.yaml")
    logger = setup_logger(config)

    tables_dir = project_root / "outputs" / "tables"
    charts_dir = project_root / "outputs" / "charts"
    report_path = project_root / "outputs" / "reports" / "summary_report.md"

    logger.info("Starting NSE quant screener Phase 3")

    full_universe = None
    cleaned_universe = None
    peer_stats = None
    ranked = None

    try:
        from src.cleaning.universe_filter import UniverseFilter
        from src.features.fundamental_features import FundamentalFeatures
        from src.features.peer_features import PeerFeatures
        from src.features.technical_features import TechnicalFeatures
        from src.loaders.fundamentals_loader import FundamentalsLoader
        from src.loaders.metadata_loader import MetadataLoader
        from src.loaders.price_loader import PriceLoader
        from src.loaders.universe_loader import UniverseLoader
        from src.scoring.score_engine import ScoreEngine

        full_universe = UniverseLoader(config=config).load()
        prices = PriceLoader(config=config).load()
        fundamentals = FundamentalsLoader(config=config).load()
        metadata = MetadataLoader(config=config).load()

        cleaned_universe = UniverseFilter(config=config).filter(full_universe)
        technicals = TechnicalFeatures(config=config).compute(prices)
        fundamental_df = FundamentalFeatures(config=config).compute(fundamentals)
        peer_stats = PeerFeatures(config=config).compute(cleaned_universe, fundamental_df, technicals)
        ranked = ScoreEngine(config=config).score(technicals, fundamental_df, peer_stats)

        if metadata is not None and not metadata.empty:
            ranked = ranked.merge(metadata, on="symbol", how="left")

    except ModuleNotFoundError as exc:
        logger.warning("Phase 3 dependencies missing (%s). Continuing with empty outputs.", exc)

    table_paths = export_tables(full_universe, cleaned_universe, peer_stats, ranked, tables_dir, logger)
    chart_paths = generate_charts(ranked, charts_dir, logger)
    report_file = generate_markdown_report(full_universe, cleaned_universe, ranked, report_path, logger)

    logger.info("Phase 3 scoring completed. Ranked rows: %d", _safe_len(ranked))
    logger.info("Exported tables: %s", ", ".join(str(p) for p in table_paths.values()))
    logger.info("Exported charts: %s", ", ".join(str(p) for p in chart_paths.values()))
    logger.info("Generated report: %s", report_file)

    _print_console_summary(full_universe, cleaned_universe, ranked, logger)


if __name__ == "__main__":
    main()
