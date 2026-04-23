from __future__ import annotations

import logging
from typing import Any


Config = dict[str, Any]


def setup_logger(config: Config | None = None) -> logging.Logger:
    """Create and configure the application logger."""
    logger = logging.getLogger("nse_quant_screener")

    configured_level = "INFO"
    if config is not None:
        logging_cfg = config.get("logging", {})
        if isinstance(logging_cfg, dict):
            configured_level = str(logging_cfg.get("level", "INFO")).upper()

    level = getattr(logging, configured_level, logging.INFO)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
