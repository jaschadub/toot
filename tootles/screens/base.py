"""Base screen class for Tootles."""

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.screen import Screen

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class BaseScreen(Screen):
    """Base class for all Tootles screens."""

    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Search"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__()
        self.app_ref = app_ref
        self.config_manager = app_ref.config_manager
        self.theme_manager = app_ref.theme_manager

    def action_command_palette(self) -> None:
        """Open fuzzy search command palette."""
        # TODO: Implement command palette screen
        self.notify("Command palette not yet implemented")

    def action_refresh(self) -> None:
        """Refresh current screen content."""
        # Override in subclasses
        self.notify("Refreshing...")

    def action_back(self) -> None:
        """Go back to previous screen."""
        if self.app.screen_stack:
            self.app.pop_screen()

    def is_configured(self) -> bool:
        """Check if the app is properly configured."""
        return self.config_manager.is_configured()

    def show_configuration_needed(self) -> None:
        """Show message about configuration being needed."""
        self.notify(
            "Please configure your Mastodon instance and access token",
            severity="warning",
        )
