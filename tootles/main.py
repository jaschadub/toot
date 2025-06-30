"""Main Tootles application."""

import logging
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Footer, Header, Static

from tootles.api.client import MastodonClient
from tootles.api.models import Status
from tootles.config.manager import ConfigManager
from tootles.media.manager import MediaManager
from tootles.screens.account import AccountScreen
from tootles.screens.explore import ExploreScreen
from tootles.screens.help import HelpScreen
from tootles.screens.notifications import NotificationsScreen
from tootles.screens.settings import SettingsScreen
from tootles.themes.manager import ThemeManager
from tootles.widgets.compose import ComposeWidget
from tootles.widgets.timeline import TimelineWidget

logger = logging.getLogger(__name__)


class TootlesApp(App):
    """Main Tootles application class."""

    CSS_PATH = "themes/builtin/standard.css"

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
        self.media_manager = MediaManager(self.config_manager.config.media)
        self.api_client: Optional[MastodonClient] = None
        self.current_timeline = "home"

    async def on_mount(self) -> None:
        """Initialize the application."""
        # Configuration is already loaded in constructor
        config = self.config_manager.config

        # Initialize API client if configured
        if config.instance_url and config.access_token:
            self.api_client = MastodonClient(
                instance_url=config.instance_url,
                access_token=config.access_token
            )

        # Load and apply theme
        await self.theme_manager.load_theme(config.theme)
        if self.theme_manager.current_css:
            self.stylesheet.add_source(self.theme_manager.current_css)

        # Load initial timeline data if we have an API client
        if self.api_client:
            await self._load_initial_timeline()
    async def _load_home_timeline(self, timeline_type: str = "home", max_id: Optional[str] = None) -> List[Status]:
        """Load statuses from the home timeline."""
        if not self.api_client:
            return []

        try:
            return await self.api_client.get_home_timeline(max_id=max_id)
        except Exception as e:
            self.notify(f"Error loading timeline: {e}", severity="error")
            return []

    async def _load_initial_timeline(self) -> None:
        """Load initial timeline data after app initialization."""
        try:
            timeline_widget = self.query_one("#main-timeline", TimelineWidget)
            timeline_widget.set_loading(True)

            statuses = await self._load_home_timeline("home", None)
            if statuses:
                timeline_widget.update_statuses(statuses)
        except Exception as e:
            # Timeline widget might not exist yet or other error
            logger.debug(f"Failed to update timeline: {e}")
        finally:
            try:
                timeline_widget = self.query_one("#main-timeline", TimelineWidget)
                timeline_widget.set_loading(False)
            except Exception as e:
                logger.debug(f"Failed to set timeline loading state: {e}")

    def compose(self) -> ComposeResult:
        """Create the main application layout."""
        yield Header()

        with Horizontal():
            # Sidebar (future feature)
            # yield Sidebar(classes="sidebar")

            # Main content area
            with Vertical(id="main-content"):
                # Check config directly since api_client isn't created yet during compose
                config = self.config_manager.config
                if config.instance_url and config.access_token:
                    yield TimelineWidget(
                        empty_message="No posts in your timeline yet. Follow some accounts to see their posts here!",
                        load_callback=self._load_home_timeline,
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
            TimelineWidget(
                empty_message="No posts in your timeline yet. Follow some accounts to see their posts here!",
                load_callback=self._load_home_timeline,
                id="main-timeline"
            )
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
            TimelineWidget(
                empty_message="No bookmarked posts yet.",
                id="main-timeline"
            )
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
            TimelineWidget(
                empty_message="No favorite posts yet.",
                id="main-timeline"
            )
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
        config = self.config_manager.config
        themes = ["standard", "dark", "light", "high-contrast"]

        current_index = themes.index(config.theme) if config.theme in themes else 0
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]

        # Update config
        config.theme = next_theme
        self.config_manager.save()

        # Apply new theme
        await self.theme_manager.load_theme(next_theme)
        if self.theme_manager.current_css:
            self.stylesheet.clear()
            self.stylesheet.add_source(self.theme_manager.current_css)

        self.notify(f"Switched to {next_theme} theme", severity="success")

    def replace_main_content(self, new_widget) -> None:
        """Replace the main content area with a new widget."""
        main_content = self.query_one("#main-content", Vertical)
        main_content.remove_children()
        main_content.mount(new_widget)

    async def reload_api_client(self) -> None:
        """Reload API client after configuration changes."""
        config = self.config_manager.config
        if config.instance_url and config.access_token:
            self.api_client = MastodonClient(
                instance_url=config.instance_url,
                access_token=config.access_token
            )

            # Replace welcome message with timeline if we were showing it
            try:
                self.query_one("#welcome-message")
                self.replace_main_content(
                    TimelineWidget(
                        empty_message="No posts in your timeline yet. Follow some accounts to see their posts here!",
                        load_callback=self._load_home_timeline,
                        id="main-timeline"
                    )
                )
            except NoMatches:
                # Welcome message not shown, nothing to replace
                pass
        else:
            self.api_client = None


def main(config_path=None):
    """Entry point for the Tootles application."""
    app = TootlesApp()
    if config_path:
        # TODO: Pass config_path to app when config loading is implemented
        pass
    app.run()


if __name__ == "__main__":
    main()
