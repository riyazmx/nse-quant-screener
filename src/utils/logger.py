from __future__ import annotations
import logging


def setup_logger() -> logging.Logger:
    """Create and configure the application logger."""
    logger = logging.getLogger("nse_quant_screener")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
