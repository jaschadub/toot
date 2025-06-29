"""Home timeline screen for Tootles."""

from typing import TYPE_CHECKING, List, Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Label, Static

from tootles.api.client import MastodonClient
from tootles.api.models import Status
from tootles.screens.base import BaseScreen
from tootles.widgets.compose import ComposeWidget
from tootles.widgets.timeline import TimelineWidget

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class HomeScreen(BaseScreen):
    """Home timeline screen showing posts from followed accounts."""

    class ComposeToggle(Message):
        """Message to toggle compose widget visibility."""
        pass

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Home Timeline"
        self.client: Optional[MastodonClient] = None
        self.timeline_widget: Optional[TimelineWidget] = None
        self.compose_widget: Optional[ComposeWidget] = None
        self.compose_visible = False

    def compose(self) -> ComposeResult:
        """Create the home screen layout."""
        if not self.is_configured():
            yield Static(
                "Welcome to Tootles!\n\n"
                "To get started, you need to configure your Mastodon instance.\n"
                "Please set your instance URL and access token in the configuration.",
                classes="welcome-message",
            )
            return

        with Horizontal():
            # Left sidebar for navigation
            with Vertical(classes="sidebar-navigation"):
                yield Label("🏠 Home", classes="nav-item nav-item--active")
                yield Label("🔔 Notifications", classes="nav-item")
                yield Label("🔍 Explore", classes="nav-item")
                yield Label("📍 Local", classes="nav-item")
                yield Label("🌐 Federated", classes="nav-item")
                yield Label("📖 Bookmarks", classes="nav-item")
                yield Label("⭐ Favorites", classes="nav-item")
                yield Label("📋 Lists", classes="nav-item")
                yield Button("✏️ Compose", id="compose-btn", classes="nav-item")
                yield Label("⚙️ Settings", classes="nav-item")

            # Main content area
            with Vertical(classes="main-content"):
                # Header with refresh button
                with Horizontal(classes="content-header"):
                    yield Label("Home Timeline", classes="screen-title")
                    yield Button("🔄 Refresh", id="refresh-btn", variant="default")

                # Timeline widget
                self.timeline_widget = TimelineWidget(
                    empty_message="No posts in your timeline yet. Follow some accounts to see their posts here!",
                    load_callback=self._load_timeline_statuses
                )
                yield self.timeline_widget

                # Compose widget (initially hidden)
                self.compose_widget = ComposeWidget()
                self.compose_widget.display = False
                yield self.compose_widget

    async def _load_timeline_statuses(self, direction: str, cursor_id: Optional[str]) -> List[Status]:
        """Load timeline statuses from the API.

        Args:
            direction: "newer" or "older"
            cursor_id: Cursor ID for pagination

        Returns:
            List of Status objects
        """
        if not self.client:
            return []

        try:
            if direction == "newer":
                return await self.client.get_home_timeline(since_id=cursor_id, limit=20)
            else:
                return await self.client.get_home_timeline(max_id=cursor_id, limit=20)
        except Exception as e:
            self.notify(f"Error loading timeline: {e}", severity="error")
            return []

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "compose-btn":
            await self._toggle_compose()
        elif event.button.id == "refresh-btn":
            await self.action_refresh()

    async def on_compose_widget_post_status(self, event: ComposeWidget.PostStatus) -> None:
        """Handle status posting from compose widget."""
        if not self.client:
            self.notify("No API client available", severity="error")
            return

        try:
            # Post the status
            new_status = await self.client.post_status(
                status=event.content,
                visibility=event.visibility,
                in_reply_to_id=event.in_reply_to_id,
                sensitive=event.sensitive,
                spoiler_text=event.spoiler_text
            )

            # Add to timeline
            if self.timeline_widget:
                self.timeline_widget.update_statuses([new_status], prepend=True)

            # Hide compose widget and clear it
            await self._hide_compose()
            self.notify("Post published successfully!", severity="information")

        except Exception as e:
            self.notify(f"Error posting status: {e}", severity="error")

    async def on_compose_widget_cancel(self, event: ComposeWidget.Cancel) -> None:
        """Handle compose cancellation."""
        await self._hide_compose()

    async def _toggle_compose(self) -> None:
        """Toggle the compose widget visibility."""
        if self.compose_visible:
            await self._hide_compose()
        else:
            await self._show_compose()

    async def _show_compose(self) -> None:
        """Show the compose widget."""
        if self.compose_widget:
            self.compose_widget.display = True
            self.compose_widget.focus()
            self.compose_visible = True

    async def _hide_compose(self) -> None:
        """Hide the compose widget."""
        if self.compose_widget:
            self.compose_widget.display = False
            self.compose_widget.clear()
            self.compose_visible = False

    async def action_refresh(self) -> None:
        """Refresh the home timeline."""
        if not self.is_configured():
            self.show_configuration_needed()
            return

        if not self.client or not self.timeline_widget:
            self.notify("Timeline not available", severity="warning")
            return

        try:
            self.timeline_widget.set_loading(True)
            self.notify("Refreshing home timeline...")
            statuses = await self.client.get_home_timeline(limit=20)
            self.timeline_widget.update_statuses(statuses)
            self.notify(f"Loaded {len(statuses)} posts", severity="information")
        except Exception as e:
            self.notify(f"Error refreshing timeline: {e}", severity="error")
        finally:
            self.timeline_widget.set_loading(False)

    def set_client(self, client: MastodonClient) -> None:
        """Set the Mastodon API client.

        Args:
            client: The MastodonClient instance
        """
        self.client = client

    async def load_initial_timeline(self) -> None:
        """Load the initial timeline when screen becomes active."""
        if self.is_configured() and self.client:
            await self.action_refresh()
