from __future__ import annotations

from pathlib import Path

from src.reports import export_tables, generate_charts, generate_markdown_report
from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger


def _print_console_summary(full_universe, cleaned_universe, ranked_stocks) -> None:
    raw_universe_size = len(full_universe) if full_universe is not None else 0
    cleaned_universe_size = len(cleaned_universe) if cleaned_universe is not None else 0

    industries_count = 0
    if cleaned_universe is not None and "industry" in getattr(cleaned_universe, "columns", []):
        industries_count = int(cleaned_universe["industry"].nunique())

    ranked_count = len(ranked_stocks) if ranked_stocks is not None else 0

    print("\n=== Phase 3 Console Summary ===")
    print(f"Raw universe size: {raw_universe_size}")
    print(f"Cleaned universe size: {cleaned_universe_size}")
    print(f"Number of industries: {industries_count}")
    print(f"Ranked stocks count: {ranked_count}")

    if ranked_stocks is None or getattr(ranked_stocks, "empty", True):
        print("Top 10 ranked stocks: no data available")
        return

    required_columns = [
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
    present_columns = [col for col in required_columns if col in ranked_stocks.columns]
    top10 = ranked_stocks.sort_values("total_score", ascending=False).head(10)
    print("\nTop 10 ranked stocks:")
    print(top10[present_columns].to_string(index=False))


def main() -> None:
    """Run Phase 3 pipeline: scoring + exports + charts + markdown report + console summary."""
    project_root = Path(__file__).resolve().parent
    config_path = project_root / "config" / "settings.yaml"

    tables_dir = project_root / "outputs" / "tables"
    charts_dir = project_root / "outputs" / "charts"
    reports_dir = project_root / "outputs" / "reports"
    report_path = reports_dir / "summary_report.md"

    config = ConfigLoader.load(config_path)
    logger = setup_logger(config)

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
        logger.warning("Phase 3 dependencies missing (%s). Continuing with empty reporting outputs.", exc)

    table_outputs = export_tables(
        full_universe=full_universe,
        cleaned_universe=cleaned_universe,
        peer_statistics=peer_stats,
        ranked_stocks=ranked,
        tables_dir=tables_dir,
        logger=logger,
    )
    chart_outputs = generate_charts(ranked_stocks=ranked, charts_dir=charts_dir, logger=logger)
    generated_report = generate_markdown_report(
        full_universe=full_universe,
        cleaned_universe=cleaned_universe,
        ranked_stocks=ranked,
        report_path=report_path,
        logger=logger,
    )

    logger.info("Phase 3 scoring completed. Ranked rows: %d", 0 if ranked is None else len(ranked))
    logger.info("Exported tables: %s", ", ".join(str(path) for path in table_outputs.values()))
    logger.info("Exported charts: %s", ", ".join(str(path) for path in chart_outputs.values()))
    logger.info("Generated report: %s", generated_report)

    _print_console_summary(full_universe=full_universe, cleaned_universe=cleaned_universe, ranked_stocks=ranked)


if __name__ == "__main__":
    main()
