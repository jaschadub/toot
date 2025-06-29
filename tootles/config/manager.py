"""Configuration manager for Tootles."""

from pathlib import Path
from typing import Optional

import tomlkit

from tootles.config.schema import TootlesConfig


class ConfigManager:
    """Manages configuration loading, saving, and validation."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "tootles"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.toml"

    def _load_config(self) -> TootlesConfig:
        """Load configuration from file or create default."""
        if not self.config_path.exists():
            config = TootlesConfig()
            self._save_config(config)
            return config

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = tomlkit.load(f)

            # Convert TOML data to config object
            config = TootlesConfig()
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            config.validate()
            return config
        except Exception:
            # If config is invalid, create a backup and use defaults
            backup_path = self.config_path.with_suffix(".toml.backup")
            if self.config_path.exists():
                self.config_path.rename(backup_path)

            config = TootlesConfig()
            self._save_config(config)
            return config

    def _save_config(self, config: TootlesConfig) -> None:
        """Save configuration to file."""
        # Convert config object to dict
        config_dict = {}
        for field_name in config.__dataclass_fields__:
            value = getattr(config, field_name)
            config_dict[field_name] = value

        # Create TOML document
        doc = tomlkit.document()
        doc.add(tomlkit.comment("Tootles Configuration"))
        doc.add(tomlkit.nl())

        # Add sections with comments
        doc.add(tomlkit.comment("Instance settings"))
        doc["instance_url"] = config_dict["instance_url"]
        doc["access_token"] = config_dict["access_token"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("UI settings"))
        doc["theme"] = config_dict["theme"]
        doc["auto_refresh"] = config_dict["auto_refresh"]
        doc["refresh_interval"] = config_dict["refresh_interval"]
        doc["show_media_previews"] = config_dict["show_media_previews"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("Timeline settings"))
        doc["timeline_limit"] = config_dict["timeline_limit"]
        doc["enable_streaming"] = config_dict["enable_streaming"]
        doc["mark_notifications_read"] = config_dict["mark_notifications_read"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("Search settings"))
        doc["search_history_size"] = config_dict["search_history_size"]
        doc["enable_fuzzy_search"] = config_dict["enable_fuzzy_search"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("Theme settings"))
        doc["theme_directory"] = config_dict["theme_directory"]
        doc["enable_theme_hot_reload"] = config_dict["enable_theme_hot_reload"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("Advanced settings"))
        doc["cache_size"] = config_dict["cache_size"]
        doc["rate_limit_requests"] = config_dict["rate_limit_requests"]
        doc["rate_limit_window"] = config_dict["rate_limit_window"]
        doc.add(tomlkit.nl())

        doc.add(tomlkit.comment("Custom timelines"))
        doc["timelines"] = config_dict["timelines"]

        # Write to file
        with open(self.config_path, "w", encoding="utf-8") as f:
            tomlkit.dump(doc, f)

    def save(self) -> None:
        """Save current configuration to file."""
        self.config.validate()
        self._save_config(self.config)

    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()

    def get_config_dir(self) -> Path:
        """Get the configuration directory."""
        return self.config_path.parent

    def is_configured(self) -> bool:
        """Check if the application is properly configured."""
        return bool(self.config.instance_url and self.config.access_token)
