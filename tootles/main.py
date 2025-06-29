"""Main entry point for Tootles application."""

import asyncio
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from tootles.api.client import MastodonClient
from tootles.config.manager import ConfigManager
from tootles.screens.home import HomeScreen
from tootles.themes.manager import ThemeManager


class TootlesApp(App):
    """Main Tootles application."""

    TITLE = "Tootles"
    SUB_TITLE = "Modern Terminal Mastodon Client"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Search"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
        Binding("h", "goto_home", "Home"),
        Binding("n", "goto_notifications", "Notifications"),
        Binding("e", "goto_explore", "Explore"),
        Binding("b", "goto_bookmarks", "Bookmarks"),
        Binding("f", "goto_favorites", "Favorites"),
        Binding("l", "goto_lists", "Lists"),
        Binding("c", "goto_compose", "Compose"),
        Binding("s", "goto_settings", "Settings"),
    ]

    def __init__(self, config_path: Optional[Path] = None):
        super().__init__()
        self.config_manager = ConfigManager(config_path)
        self.theme_manager = ThemeManager(self.config_manager)
        self.api_client: Optional[MastodonClient] = None
        self._current_screen_name = "home"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(id="main-content")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the application."""
        # Load and apply theme
        await self.theme_manager.load_theme(self.config_manager.config.theme)

        # Initialize API client if configured
        if self.config_manager.config.instance_url and self.config_manager.config.access_token:
            self.api_client = MastodonClient(
                instance_url=self.config_manager.config.instance_url,
                access_token=self.config_manager.config.access_token
            )

        # Push initial screen
        self.push_screen(HomeScreen(self))

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_command_palette(self) -> None:
        """Open command palette."""
        # TODO: Implement command palette
        pass

    def action_refresh(self) -> None:
        """Refresh current screen."""
        if hasattr(self.screen, "refresh"):
            self.screen.refresh()

    def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current_theme = self.config_manager.config.theme
        new_theme = "dark" if current_theme == "light" else "light"
        self.config_manager.config.theme = new_theme
        asyncio.create_task(self.theme_manager.load_theme(new_theme))

    def action_goto_home(self) -> None:
        """Navigate to home timeline."""
        if self._current_screen_name != "home":
            self.push_screen(HomeScreen(self))
            self._current_screen_name = "home"

    def action_goto_notifications(self) -> None:
        """Navigate to notifications."""
        # TODO: Implement notifications screen
        pass

    def action_goto_explore(self) -> None:
        """Navigate to explore."""
        # TODO: Implement explore screen
        pass

    def action_goto_bookmarks(self) -> None:
        """Navigate to bookmarks."""
        # TODO: Implement bookmarks screen
        pass

    def action_goto_favorites(self) -> None:
        """Navigate to favorites."""
        # TODO: Implement favorites screen
        pass

    def action_goto_lists(self) -> None:
        """Navigate to lists."""
        # TODO: Implement lists screen
        pass

    def action_goto_compose(self) -> None:
        """Navigate to compose."""
        # TODO: Implement compose screen
        pass

    def action_goto_settings(self) -> None:
        """Navigate to settings."""
        # TODO: Implement settings screen
        pass


def run_app(config_path: Optional[Path] = None) -> None:
    """Run the Tootles application."""
    app = TootlesApp(config_path)
    app.run()


if __name__ == "__main__":
    run_app()
