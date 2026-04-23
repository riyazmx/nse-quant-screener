from __future__ import annotations

from pathlib import Path

from src.loaders.fundamentals_loader import FundamentalsLoader
from src.loaders.metadata_loader import MetadataLoader
from src.loaders.price_loader import PriceLoader
from src.loaders.universe_loader import UniverseLoader
from src.utils.config import ConfigLoader
from src.utils.logger import setup_logger


def main() -> None:
    """Run the Phase 1 scaffold entrypoint for the NSE quant screener."""
    project_root = Path(__file__).resolve().parent
    config_path = project_root / "config" / "settings.yaml"

    config = ConfigLoader.load(config_path)
    logger = setup_logger(config)

    logger.info("Starting NSE quant screener (Phase 1 scaffold)")
    logger.info("Using config file: %s", config_path)

    universe = UniverseLoader(config=config).load()
    prices = PriceLoader(config=config).load()
    fundamentals = FundamentalsLoader(config=config).load()
    metadata = MetadataLoader(config=config).load()

    logger.info("Universe rows: %d", len(universe))
    logger.info("Price rows: %d", len(prices))
    logger.info("Fundamentals rows: %d", len(fundamentals))
    logger.info("Metadata rows: %d", len(metadata))
    logger.info("Phase 1 scaffold is ready.")


if __name__ == "__main__":
    main()
