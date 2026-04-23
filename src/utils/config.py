from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

Config = dict[str, Any]


def _load_with_pyyaml(config_path: Path) -> Config | None:
    """Load YAML with PyYAML when the dependency is available."""
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return None

    with config_path.open("r", encoding="utf-8") as handle:
        parsed = yaml.safe_load(handle)

    if parsed is None:
        return {}

    if not isinstance(parsed, dict):
        raise ValueError("Top-level configuration must be a mapping/object.")

    return parsed


def _load_yaml_subset_without_dependency(config_path: Path) -> Config:
    """Fallback loader for JSON-compatible YAML content."""
    raw_text = config_path.read_text(encoding="utf-8")
    parsed = json.loads(raw_text)

    if not isinstance(parsed, dict):
        raise ValueError("Top-level configuration must be a mapping/object.")

    return parsed


class ConfigLoader:
    """Load application configuration from config/settings.yaml."""

    @staticmethod
    def load(config_path: Path) -> Config:
        """Load a configuration file using YAML, with JSON-compatible fallback."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        config = _load_with_pyyaml(config_path)
        if config is not None:
            return config

        logging.getLogger("nse_quant_screener").warning(
            "PyYAML is not installed; using JSON-compatible parser for %s",
            config_path,
        )
        return _load_yaml_subset_without_dependency(config_path)
