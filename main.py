from pathlib import Path

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger
from src.loaders.universe_loader import UniverseLoader
from src.loaders.price_loader import PriceLoader
from src.loaders.fundamentals_loader import FundamentalsLoader
from src.loaders.metadata_loader import MetadataLoader
from src.features.fundamental_features import FundamentalFeatures
from src.features.peer_features import PeerFeatures
from src.features.technical_features import TechnicalFeatures
from src.scoring.score_engine import ScoreEngine
from src.cleaning.universe_filter import UniverseFilter


def main() -> None:
    """Entry point for the NSE quant screener application."""
    config_path = Path(__file__).resolve().parent / "config" / "settings.yaml"
    logger = setup_logger()

    logger.info("Starting NSE quant screener Phase 2")

    config = ConfigLoader.load(config_path)
    universe_loader = UniverseLoader(config=config)
    price_loader = PriceLoader(config=config)
    fundamentals_loader = FundamentalsLoader(config=config)
    metadata_loader = MetadataLoader(config=config)

    universe = universe_loader.load()
    prices = price_loader.load()
    fundamentals = fundamentals_loader.load()
    metadata = metadata_loader.load()

    filtered_universe = UniverseFilter(config=config).filter(universe)

    technicals = TechnicalFeatures(config=config).compute(prices)
    fundamental_df = FundamentalFeatures(config=config).compute(fundamentals)
    peer_stats = PeerFeatures(config=config).compute(universe, fundamental_df, technicals)
    scored = ScoreEngine(config=config).score(technicals, fundamental_df, peer_stats)

    output_path = Path(__file__).resolve().parent / "outputs" / "tables" / "scorecard.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_path, index=False)

    logger.info("Phase 2 scoring completed. Results saved to %s", output_path)
    logger.info("Top ranked symbols:\n%s", scored.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
