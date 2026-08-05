import os
import pytest
from clearfx.core.config import (
    ClearFXConfig, WeightConfig, load_config, save_config,
    _dict_to_toml, _toml_value
)

def test_default_config():
    config = ClearFXConfig()
    assert config.enabled is True
    assert config.duration_ms == 1100
    assert config.fps == 30
    assert isinstance(config.weights, WeightConfig)

def test_config_from_dict():
    data = {
        "enabled": False,
        "duration_ms": 500,
        "weights": {"favorites": 3.0}
    }
    config = ClearFXConfig.from_dict(data)
    assert config.enabled is False
    assert config.duration_ms == 500
    assert config.weights.favorites == 3.0

def test_dict_to_toml():
    data = {
        "enabled": True,
        "history_size": 10,
        "nested": {"key": "value"},
        "items": [1, 2, 3]
    }
    toml_str = _dict_to_toml(data)
    assert "enabled = true" in toml_str
    assert "history_size = 10" in toml_str
    assert "[nested]" in toml_str
    assert 'key = "value"' in toml_str
    assert "items = [1, 2, 3]" in toml_str

def test_toml_value():
    assert _toml_value(True) == "true"
    assert _toml_value(False) == "false"
    assert _toml_value(42) == "42"
    assert _toml_value(3.14) == "3.14"
    assert _toml_value("test") == '"test"'

def test_load_config_env_override(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    config = load_config()
    assert config.monochrome is True
