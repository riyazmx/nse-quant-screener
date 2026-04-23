from __future__ import annotations
from pathlib import Path
from typing import Any

import yaml


Config = dict[str, Any]


class ConfigLoader:
    """Loads YAML configuration for the NSE quant screener."""

    @staticmethod
    def load(config_path: Path) -> Config:
        """Load a YAML configuration file from a path."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)

        if config is None:
            return {}

        return config
