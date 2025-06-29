"""Enhanced theme manager for Tootles with CSS loading and validation."""

import asyncio
import importlib.resources
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from tootles.config.manager import ConfigManager


class ThemeValidationError(Exception):
    """Raised when theme validation fails."""
    pass


class ThemeFileWatcher(FileSystemEventHandler):
    """File system watcher for theme hot-reloading."""

    def __init__(self, theme_manager: "ThemeManager"):
        self.theme_manager = theme_manager

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith('.css'):
            theme_path = Path(event.src_path)
            theme_name = theme_path.stem
            if theme_name == self.theme_manager.current_theme:
                asyncio.create_task(self.theme_manager.reload_current_theme())


class ThemeManager:
    """Enhanced theme manager with CSS loading, validation, and hot-reloading."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_theme: Optional[str] = None
        self.current_css: Optional[str] = None
        self.builtin_themes = self._discover_builtin_themes()
        self.user_themes = self._discover_user_themes()
        self._file_observer: Optional[Observer] = None
        self._required_selectors = {
            ".app-container",
            ".status-item",
            ".timeline-widget",
            ".compose-widget",
            ".button",
            ".input-field"
        }
        self._css_variables = {
            "$background", "$surface", "$primary", "$text", "$text-muted",
            "$text-disabled", "$border", "$error", "$warning", "$success",
            "$accent", "$text-inverse", "$primary-muted", "$surface-lighten-1",
            "$surface-darken-1", "$surface-darken-2", "$primary-lighten-1"
        }

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

    def get_theme_info(self, theme_name: str) -> Dict[str, str]:
        """Get theme information including description and author."""
        theme_path = self.get_theme_path(theme_name)
        if not theme_path:
            return {
                "name": theme_name,
                "description": "Theme not found",
                "author": "Unknown"
            }

        try:
            with open(theme_path, encoding="utf-8") as f:
                content = f.read()

            # Extract theme info from CSS comments
            info = {"name": theme_name, "description": "", "author": ""}

            # Look for theme description in first comment block
            comment_match = re.search(r'/\*\s*(.*?)\s*\*/', content, re.DOTALL)
            if comment_match:
                comment_text = comment_match.group(1)
                lines = [line.strip() for line in comment_text.split('\n')]

                # First non-empty line is usually the theme name/description
                for line in lines:
                    if line and not line.startswith('*'):
                        info["description"] = line
                        break

                # Look for author info
                for line in lines:
                    if "author:" in line.lower() or "by:" in line.lower():
                        info["author"] = line.split(":", 1)[1].strip()
                        break

            return info
        except Exception:
            return {
                "name": theme_name,
                "description": "Error reading theme",
                "author": "Unknown"
            }

    async def load_theme(self, theme_name: str) -> bool:
        """Load and apply a theme."""
        theme_path = self.get_theme_path(theme_name)
        if not theme_path:
            raise ThemeValidationError(f"Theme '{theme_name}' not found")

        try:
            # Read and validate CSS
            css_content = await self._read_css_file(theme_path)
            validation_result = self.validate_theme_content(css_content)

            if not validation_result[0]:
                raise ThemeValidationError(
                    f"Theme validation failed: {validation_result[1]}"
                )

            # Apply the theme
            self.current_theme = theme_name
            self.current_css = css_content

            # Start file watching for hot-reload if enabled
            if self.config_manager.config.enable_theme_hot_reload:
                await self._start_file_watching()

            return True

        except Exception as e:
            raise ThemeValidationError(f"Error loading theme '{theme_name}': {e}") from e

    async def _read_css_file(self, theme_path: Path) -> str:
        """Read CSS file content asynchronously."""
        try:
            if hasattr(theme_path, 'read_text'):
                # For importlib.resources paths
                return theme_path.read_text(encoding='utf-8')
            else:
                # For regular file paths
                with open(theme_path, encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            raise ThemeValidationError(f"Error reading CSS file: {e}") from e

    def validate_theme_content(self, css_content: str) -> Tuple[bool, str]:
        """Validate CSS theme content."""
        if not css_content.strip():
            return False, "Theme file is empty"

        # Check for required selectors
        missing_selectors = []
        for selector in self._required_selectors:
            if selector not in css_content:
                missing_selectors.append(selector)

        if missing_selectors:
            return False, f"Missing required selectors: {', '.join(missing_selectors)}"

        # Basic CSS syntax validation
        try:
            # Check for balanced braces
            open_braces = css_content.count('{')
            close_braces = css_content.count('}')
            if open_braces != close_braces:
                return False, (
                    f"Unbalanced braces: {open_braces} opening, {close_braces} closing"
                )

            # Check for basic CSS structure
            if not re.search(r'[.#][\w-]+\s*\{[^}]*\}', css_content):
                return False, "No valid CSS rules found"

        except Exception as e:
            return False, f"CSS syntax error: {e}"

        return True, "Theme validation successful"

    def validate_theme(self, theme_path: Path) -> bool:
        """Validate a theme file."""
        if not theme_path.exists():
            return False

        try:
            with open(theme_path, encoding="utf-8") as f:
                content = f.read()
            return self.validate_theme_content(content)[0]
        except Exception:
            return False

    async def reload_current_theme(self) -> bool:
        """Reload the current theme (useful for development)."""
        if self.current_theme:
            try:
                await self.load_theme(self.current_theme)
                return True
            except Exception:
                return False
        return False

    def create_user_theme_directory(self) -> Path:
        """Create user theme directory if it doesn't exist."""
        theme_dir = self.config_manager.config.get_theme_directory()
        theme_dir.mkdir(parents=True, exist_ok=True)
        return theme_dir

    def refresh_user_themes(self) -> None:
        """Refresh the list of user themes."""
        self.user_themes = self._discover_user_themes()

    async def _start_file_watching(self) -> None:
        """Start watching theme files for changes."""
        if self._file_observer:
            self._file_observer.stop()

        theme_dir = self.config_manager.config.get_theme_directory()
        if theme_dir.exists():
            event_handler = ThemeFileWatcher(self)
            self._file_observer = Observer()
            self._file_observer.schedule(event_handler, str(theme_dir), recursive=False)
            self._file_observer.start()

    def stop_file_watching(self) -> None:
        """Stop watching theme files."""
        if self._file_observer:
            self._file_observer.stop()
            self._file_observer.join()
            self._file_observer = None

    def export_theme_template(self, output_path: Path) -> None:
        """Export the community theme template to a file."""
        template_path = self.get_theme_path("community-template")
        if template_path:
            try:
                if hasattr(template_path, 'read_text'):
                    content = template_path.read_text(encoding='utf-8')
                else:
                    with open(template_path, encoding="utf-8") as f:
                        content = f.read()

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                raise ThemeValidationError(f"Error exporting template: {e}") from e

    def get_css_variables_used(self, theme_name: str) -> Set[str]:
        """Get list of CSS variables used in a theme."""
        theme_path = self.get_theme_path(theme_name)
        if not theme_path:
            return set()

        try:
            with open(theme_path, encoding="utf-8") as f:
                content = f.read()

            # Find all CSS variables used
            variables = set()
            for var in self._css_variables:
                if var in content:
                    variables.add(var)

            return variables
        except Exception:
            return set()

    def __del__(self):
        """Cleanup file watcher on destruction."""
        self.stop_file_watching()
