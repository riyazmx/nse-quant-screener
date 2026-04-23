from pathlib import Path

from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger
from src.loaders.universe_loader import UniverseLoader
from src.loaders.price_loader import PriceLoader
from src.loaders.fundamentals_loader import FundamentalsLoader
from src.loaders.metadata_loader import MetadataLoader
from src.cleaning.universe_filter import UniverseFilter


def main() -> None:
    """Entry point for the NSE quant screener application."""
    config_path = Path(__file__).resolve().parent / "config" / "settings.yaml"
    logger = setup_logger()

    logger.info("Starting NSE quant screener Phase 1")

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

    logger.info("Loaded universe: %s", universe)
    logger.info("Loaded prices: %s", prices)
    logger.info("Loaded fundamentals: %s", fundamentals)
    logger.info("Loaded metadata: %s", metadata)
    logger.info("Filtered universe: %s", filtered_universe)

    logger.info("Phase 1 scaffold completed successfully.")


if __name__ == "__main__":
    main()
