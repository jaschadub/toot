"""Notifications screen for Tootles."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from tootles.screens.base import BaseScreen
from tootles.widgets.timeline import TimelineWidget

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class NotificationsScreen(BaseScreen):
    """Screen for displaying user notifications."""

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Notifications"

    def compose(self) -> ComposeResult:
        """Create the notifications screen layout."""
        with Vertical():
            # Header
            with Horizontal(classes="notifications-header"):
                yield Static("Notifications", classes="screen-title")
                with Horizontal(classes="header-actions"):
                    yield Button("Mark All Read", id="mark-read-btn", variant="default")
                    yield Button("Refresh", id="refresh-btn", variant="primary")

            # Filter Tabs
            with Horizontal(classes="filter-tabs"):
                yield Button("All", id="filter-all", variant="primary", classes="filter-tab active")
                yield Button("Mentions", id="filter-mentions", variant="default", classes="filter-tab")
                yield Button("Follows", id="filter-follows", variant="default", classes="filter-tab")
                yield Button("Boosts", id="filter-boosts", variant="default", classes="filter-tab")
                yield Button("Favorites", id="filter-favorites", variant="default", classes="filter-tab")

            # Notifications Timeline
            yield TimelineWidget(
                self.app_ref,
                timeline_type="notifications",
                id="notifications-timeline",
                media_manager=getattr(self.app_ref, 'media_manager', None)
            )

    async def on_mount(self) -> None:
        """Load notifications when screen is mounted."""
        await self.load_notifications()

    async def load_notifications(self, notification_type: str = "all") -> None:
        """Load notifications from the API."""
        try:
            timeline = self.query_one("#notifications-timeline", TimelineWidget)
            await timeline.load_timeline()

        except Exception as e:
            self.app.notify(f"Failed to load notifications: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "refresh-btn":
            await self.load_notifications()
        elif event.button.id == "mark-read-btn":
            await self.mark_all_read()
        elif event.button.id.startswith("filter-"):
            await self.handle_filter_change(event.button)

    async def handle_filter_change(self, button: Button) -> None:
        """Handle notification filter changes."""
        # Update active filter tab
        for tab in self.query(".filter-tab"):
            tab.remove_class("active")
            tab.variant = "default"

        button.add_class("active")
        button.variant = "primary"

        # Extract filter type from button ID
        filter_type = button.id.replace("filter-", "")
        await self.load_notifications(filter_type)

    async def mark_all_read(self) -> None:
        """Mark all notifications as read."""
        try:
            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            await self.app_ref.api_client.mark_notifications_read()
            self.app.notify("All notifications marked as read", severity="success")
            await self.load_notifications()

        except Exception as e:
            self.app.notify(f"Failed to mark notifications as read: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh notifications (keyboard shortcut)."""
        self.run_worker(self.load_notifications())

    DEFAULT_CSS = """
    NotificationsScreen {
        background: $surface;
    }

    .notifications-header {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $border;
    }

    .screen-title {
        width: 1fr;
        text-style: bold;
        color: $primary;
        content-align: left middle;
    }

    .header-actions {
        width: auto;
        height: 3;
    }

    .header-actions Button {
        margin-left: 1;
    }

    .filter-tabs {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $border;
    }

    .filter-tab {
        margin-right: 1;
        min-width: 10;
    }

    .filter-tab.active {
        background: $primary;
        color: $text-primary;
    }

    #notifications-timeline {
        height: 1fr;
    }
    """
