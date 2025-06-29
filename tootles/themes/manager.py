"""Theme manager for Tootles."""

import importlib.resources
from pathlib import Path
from typing import Dict, List, Optional

from tootles.config.manager import ConfigManager


class ThemeManager:
    """Manages theme loading, validation, and application."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_theme: Optional[str] = None
        self.builtin_themes = self._discover_builtin_themes()
        self.user_themes = self._discover_user_themes()

    def _discover_builtin_themes(self) -> Dict[str, Path]:
        """Discover built-in themes."""
        themes = {}
        try:
            # Get builtin themes from package resources
            builtin_path = importlib.resources.files("tootles.themes.builtin")
            if builtin_path.is_dir():
                for theme_file in builtin_path.iterdir():
                    if theme_file.name.endswith(".css"):
                        theme_name = theme_file.name[:-4]  # Remove .css extension
                        themes[theme_name] = theme_file
        except (ImportError, FileNotFoundError):
            # Fallback if package resources not available
            pass

        # Add default themes if not found
        if not themes:
            themes = {
                "default": None,
                "dark": None,
                "light": None,
            }

        return themes

    def _discover_user_themes(self) -> Dict[str, Path]:
        """Discover user themes."""
        themes = {}
        theme_dir = self.config_manager.config.get_theme_directory()

        if theme_dir.exists():
            for theme_file in theme_dir.glob("*.css"):
                theme_name = theme_file.stem
                themes[theme_name] = theme_file

        return themes

    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        all_themes = set()
        all_themes.update(self.builtin_themes.keys())
        all_themes.update(self.user_themes.keys())
        return sorted(all_themes)

    def get_theme_path(self, theme_name: str) -> Optional[Path]:
        """Get the path to a theme file."""
        # Check user themes first (they override builtin)
        if theme_name in self.user_themes:
            return self.user_themes[theme_name]

        # Check builtin themes
        if theme_name in self.builtin_themes:
            return self.builtin_themes[theme_name]

        return None

    async def load_theme(self, theme_name: str) -> bool:
        """Load and apply a theme."""
        # For now, we'll use Textual's built-in theme support
        # In a full implementation, we would load CSS files and apply them
        self.current_theme = theme_name

        # TODO: Implement actual CSS loading and application
        # This would involve:
        # 1. Reading the CSS file
        # 2. Parsing and validating the CSS
        # 3. Applying it to the current app instance

        return True

    def reload_current_theme(self) -> bool:
        """Reload the current theme (useful for development)."""
        if self.current_theme:
            return self.load_theme(self.current_theme)
        return False

    def validate_theme(self, theme_path: Path) -> bool:
        """Validate a theme file."""
        if not theme_path.exists():
            return False

        try:
            with open(theme_path, encoding="utf-8") as f:
                content = f.read()

            # Basic validation - check if it's valid CSS
            # In a full implementation, we would use a CSS parser
            if not content.strip():
                return False

            # Check for required selectors (basic validation)
            required_selectors = [".app-container", ".status-item"]
            for selector in required_selectors:
                if selector not in content:
                    return False

            return True
        except Exception:
            return False

    def create_user_theme_directory(self) -> Path:
        """Create user theme directory if it doesn't exist."""
        theme_dir = self.config_manager.config.get_theme_directory()
        theme_dir.mkdir(parents=True, exist_ok=True)
        return theme_dir

    def refresh_user_themes(self) -> None:
        """Refresh the list of user themes."""
        self.user_themes = self._discover_user_themes()
