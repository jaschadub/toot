"""Main Tootles application."""

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from tootles.api.client import MastodonClient
from tootles.config.manager import ConfigManager
from tootles.screens.account import AccountScreen
from tootles.screens.explore import ExploreScreen
from tootles.screens.help import HelpScreen
from tootles.screens.notifications import NotificationsScreen
from tootles.screens.settings import SettingsScreen
from tootles.themes.manager import ThemeManager
from tootles.widgets.compose import ComposeWidget
from tootles.widgets.timeline import TimelineWidget


class TootlesApp(App):
    """Main Tootles application class."""

    CSS_PATH = "themes/builtin/default.css"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+p", "command_palette", "Command Palette"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
        Binding("h", "show_home", "Home"),
        Binding("n", "show_notifications", "Notifications"),
        Binding("e", "show_explore", "Explore"),
        Binding("b", "show_bookmarks", "Bookmarks"),
        Binding("f", "show_favorites", "Favorites"),
        Binding("l", "show_lists", "Lists"),
        Binding("c", "compose", "Compose"),
        Binding("s", "show_settings", "Settings"),
        Binding("a", "show_account", "Account"),
        Binding("question_mark", "show_help", "Help"),
        Binding("escape", "go_back", "Back"),
    ]

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager(self.config_manager)
        self.api_client: Optional[MastodonClient] = None
        self.current_timeline = "home"

    async def on_mount(self) -> None:
        """Initialize the application."""
        # Load configuration
        await self.config_manager.load_config()

        # Initialize API client if configured
        config = self.config_manager.get_config()
        if config.mastodon.instance_url and config.mastodon.access_token:
            self.api_client = MastodonClient(
                instance_url=config.mastodon.instance_url,
                access_token=config.mastodon.access_token
            )

        # Load and apply theme
        await self.theme_manager.load_theme(config.ui.theme)
        if self.theme_manager.current_theme_css:
            self.stylesheet.add_source(self.theme_manager.current_theme_css)

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()

        with Horizontal():
            # Sidebar (future feature)
            # yield Sidebar(classes="sidebar")

            # Main content area
            with Vertical(id="main-content"):
                if self.api_client:
                    yield TimelineWidget(
                        self,
                        timeline_type="home",
                        id="main-timeline"
                    )
                else:
                    yield Static(
                        "Welcome to Tootles!\n\n"
                        "Please configure your Mastodon instance in Settings (S) "
                        "to get started.",
                        id="welcome-message",
                        classes="welcome"
                    )

        yield Footer()

    # Navigation Actions
    def action_show_home(self) -> None:
        """Show home timeline."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.current_timeline = "home"
        self.replace_main_content(
            TimelineWidget(self, timeline_type="home", id="main-timeline")
        )

    def action_show_notifications(self) -> None:
        """Show notifications screen."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.push_screen(NotificationsScreen(self))

    def action_show_explore(self) -> None:
        """Show explore screen."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.push_screen(ExploreScreen(self))

    def action_show_bookmarks(self) -> None:
        """Show bookmarks timeline."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.current_timeline = "bookmarks"
        self.replace_main_content(
            TimelineWidget(self, timeline_type="bookmarks", id="main-timeline")
        )

    def action_show_favorites(self) -> None:
        """Show favorites timeline."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.current_timeline = "favorites"
        self.replace_main_content(
            TimelineWidget(self, timeline_type="favorites", id="main-timeline")
        )

    def action_show_lists(self) -> None:
        """Show lists (placeholder)."""
        self.notify("Lists feature not yet implemented", severity="information")

    def action_compose(self) -> None:
        """Show compose modal."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        compose_widget = ComposeWidget(self)
        self.push_screen(compose_widget)

    def action_show_settings(self) -> None:
        """Show settings screen."""
        self.push_screen(SettingsScreen(self))

    def action_show_account(self) -> None:
        """Show account management screen."""
        if not self.api_client:
            self.notify(
                "Please configure your Mastodon instance first",
                severity="warning"
            )
            return

        self.push_screen(AccountScreen(self))

    def action_show_help(self) -> None:
        """Show help screen."""
        self.push_screen(HelpScreen(self))

    def action_go_back(self) -> None:
        """Go back to previous screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()

    # Utility Actions
    def action_refresh(self) -> None:
        """Refresh current content."""
        try:
            timeline = self.query_one("#main-timeline", TimelineWidget)
            self.run_worker(timeline.load_timeline())
        except Exception:
            self.notify("Nothing to refresh", severity="information")

    async def action_toggle_theme(self) -> None:
        """Toggle between available themes."""
        config = self.config_manager.get_config()
        themes = ["default", "dark", "light", "high-contrast"]

        current_index = themes.index(config.ui.theme) if config.ui.theme in themes else 0
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]

        # Update config
        config.ui.theme = next_theme
        await self.config_manager.save_config()

        # Apply new theme
        await self.theme_manager.load_theme(next_theme)
        if self.theme_manager.current_theme_css:
            self.stylesheet.clear()
            self.stylesheet.add_source(self.theme_manager.current_theme_css)

        self.notify(f"Switched to {next_theme} theme", severity="success")

    def replace_main_content(self, new_widget) -> None:
        """Replace the main content area with a new widget."""
        main_content = self.query_one("#main-content", Vertical)
        main_content.remove_children()
        main_content.mount(new_widget)

    async def reload_api_client(self) -> None:
        """Reload API client after configuration changes."""
        config = self.config_manager.get_config()
        if config.mastodon.instance_url and config.mastodon.access_token:
            self.api_client = MastodonClient(
                instance_url=config.mastodon.instance_url,
                access_token=config.mastodon.access_token
            )

            # Replace welcome message with timeline if we were showing it
            try:
                self.query_one("#welcome-message")
                self.replace_main_content(
                    TimelineWidget(self, timeline_type="home", id="main-timeline")
                )
            except Exception:
                pass  # Welcome message not shown
        else:
            self.api_client = None


def main():
    """Entry point for the Tootles application."""
    app = TootlesApp()
    app.run()


if __name__ == "__main__":
    main()
