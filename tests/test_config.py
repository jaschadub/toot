"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest

from tootles.config.manager import ConfigManager
from tootles.config.schema import TootlesConfig


def test_config_creation():
    """Test basic config creation."""
    config = TootlesConfig()
    assert config.theme == "default"
    assert config.auto_refresh is True
    assert config.refresh_interval == 60


def test_config_validation():
    """Test config validation."""
    config = TootlesConfig()
    config.validate()  # Should not raise

    # Test invalid refresh interval
    config.refresh_interval = -1
    with pytest.raises(ValueError):
        config.validate()


def test_config_manager():
    """Test config manager basic functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.toml"
        manager = ConfigManager(config_path)

        # Should create default config
        config = manager.config
        assert isinstance(config, TootlesConfig)
        assert config.theme == "default"

        # Should save and reload config
        config.theme = "dark"
        manager.save()

        manager.reload()
        assert manager.config.theme == "dark"
