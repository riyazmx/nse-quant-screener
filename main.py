from __future__ import annotations

from pathlib import Path

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger


def main() -> None:
    """Run Phase 2 pipeline and persist the ranked scorecard."""
    project_root = Path(__file__).resolve().parent
    config_path = project_root / "config" / "settings.yaml"

    config = ConfigLoader.load(config_path)
    logger = setup_logger(config)

    logger.info("Starting NSE quant screener Phase 2")

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
    except ModuleNotFoundError as exc:
        logger.warning("Phase 2 dependencies missing (%s). Install requirements and rerun.", exc)
        return

    universe = UniverseLoader(config=config).load()
    prices = PriceLoader(config=config).load()
    fundamentals = FundamentalsLoader(config=config).load()
    metadata = MetadataLoader(config=config).load()

    filtered_universe = UniverseFilter(config=config).filter(universe)

    technicals = TechnicalFeatures(config=config).compute(prices)
    fundamental_df = FundamentalFeatures(config=config).compute(fundamentals)
    peer_stats = PeerFeatures(config=config).compute(filtered_universe, fundamental_df, technicals)

    ranked = ScoreEngine(config=config).score(technicals, fundamental_df, peer_stats)

    if not metadata.empty:
        ranked = ranked.merge(metadata, on="symbol", how="left")

    output_path = project_root / "outputs" / "tables" / "scorecard.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(output_path, index=False)

    logger.info("Phase 2 scoring completed. Results saved to %s", output_path)
    logger.info("Top ranked symbols:\n%s", ranked.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
