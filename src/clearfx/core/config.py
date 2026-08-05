"""ClearFX configuration management.

Uses platformdirs for platform-specific config/data/cache paths.
Config is stored as TOML in the user's config directory.
"""
from __future__ import annotations

import json
import os
import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import platformdirs

APP_NAME = "clearfx"
APP_AUTHOR = "clearfx"


@dataclass
class WeightConfig:
    """Weight configuration for random selection."""
    favorites: float = 2.0
    newly_installed: float = 1.25
    builtins: float = 1.0
    community: float = 1.0


@dataclass
class ClearFXConfig:
    """Main ClearFX configuration."""
    enabled: bool = True
    duration_ms: int = 1100
    fps: int = 30
    reduced_motion: bool = False
    ascii_only: bool = False
    monochrome: bool = False
    attribution_position: str = "auto"
    history_size: int = 8
    source: str = "all"
    skip_on_keypress: bool = True
    clear_after: bool = True
    favorites: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    tag_filters: list[str] = field(default_factory=list)
    creator_filters: list[str] = field(default_factory=list)
    wrapped_commands: dict[str, str] = field(default_factory=dict)
    weights: WeightConfig = field(default_factory=WeightConfig)
    marketplace_url: str = "https://marketplace.clearfx.io"
    debug: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClearFXConfig:
        """Create config from a dictionary."""
        if "weights" in data and isinstance(data["weights"], dict):
            data["weights"] = WeightConfig(**data["weights"])
        if "wrapped_commands" in data and isinstance(data["wrapped_commands"], list):
            data["wrapped_commands"] = {cmd: "" for cmd in data["wrapped_commands"]}
        valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


def get_config_dir() -> Path:
    """Get the config directory path."""
    return Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))


def get_data_dir() -> Path:
    """Get the data directory path."""
    return Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    return Path(platformdirs.user_cache_dir(APP_NAME, APP_AUTHOR))


def get_config_path() -> Path:
    """Get the config file path."""
    return get_config_dir() / "config.toml"


def load_config() -> ClearFXConfig:
    """Load configuration from TOML file, or return defaults."""
    # Check NO_COLOR environment variable
    config = ClearFXConfig()

    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            config = ClearFXConfig.from_dict(data)
        except Exception:
            pass

    # Environment overrides
    if os.environ.get("NO_COLOR"):
        config.monochrome = True

    return config


def save_config(config: ClearFXConfig) -> None:
    """Save configuration to TOML file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = get_config_path()

    data = asdict(config)
    toml_str = _dict_to_toml(data)
    config_path.write_text(toml_str)


def _dict_to_toml(data: dict[str, Any], prefix: str = "") -> str:
    """Simple dict-to-TOML serializer (no external dependency)."""
    lines: list[str] = []
    tables: list[tuple[str, dict[str, Any]]] = []

    for key, value in data.items():
        if isinstance(value, dict):
            tables.append((key, value))
        elif isinstance(value, list):
            items = ", ".join(_toml_value(v) for v in value)
            lines.append(f"{key} = [{items}]")
        else:
            lines.append(f"{key} = {_toml_value(value)}")

    for key, table in tables:
        full_key = f"{prefix}.{key}" if prefix else key
        lines.append("")
        lines.append(f"[{full_key}]")
        lines.append(_dict_to_toml(table, full_key))

    return "\n".join(lines)


def _toml_value(value: Any) -> str:
    """Convert a Python value to a TOML value string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    else:
        return f'"{value}"'
