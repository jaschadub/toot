"""Timeline widget for displaying a scrollable list of statuses."""

from typing import Awaitable, Callable, List, Optional

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label

from ..api.models import Status
from ..media.manager import MediaManager
from .status import StatusWidget


class Timeline(Widget):
    """A scrollable timeline widget for displaying statuses."""

    DEFAULT_CSS = """
    Timeline {
        height: 1fr;
        width: 1fr;
    }

    Timeline VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    Timeline .empty-message {
        height: 3;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
    }

    Timeline .loading-message {
        height: 3;
        content-align: center middle;
        color: $text-muted;
    }
    """

    class StatusSelected(Message):
        """Message sent when a status is selected."""

        def __init__(self, status: Status) -> None:
            self.status = status
            super().__init__()

    class LoadMore(Message):
        """Message sent when more statuses should be loaded."""

        def __init__(self, direction: str = "older") -> None:
            self.direction = direction  # "older" or "newer"
            super().__init__()

    def __init__(
        self,
        statuses: Optional[List[Status]] = None,
        empty_message: str = "No statuses to display",
        app_ref=None,
        media_manager: Optional[MediaManager] = None,
        **kwargs
    ):
        """Initialize the timeline widget.

        Args:
            statuses: Initial list of statuses to display
            empty_message: Message to show when timeline is empty
            app_ref: Reference to the main application
            media_manager: MediaManager instance for handling media previews
        """
        super().__init__(**kwargs)
        self._statuses: List[Status] = statuses or []
        self._empty_message = empty_message
        self._loading = False
        self._status_widgets: List[StatusWidget] = []
        self.app_ref = app_ref
        self.media_manager = media_manager or getattr(app_ref, 'media_manager', None)

    def compose(self) -> ComposeResult:
        """Compose the timeline layout."""
        with VerticalScroll():
            if self._loading:
                yield Label("Loading...", classes="loading-message")
            elif not self._statuses:
                yield Label(self._empty_message, classes="empty-message")
            else:
                for status in self._statuses:
                    status_widget = StatusWidget(status, self.app_ref, media_manager=self.media_manager)
                    self._status_widgets.append(status_widget)
                    yield status_widget

    def set_loading(self, loading: bool) -> None:
        """Set the loading state of the timeline.

        Args:
            loading: Whether the timeline is currently loading
        """
        self._loading = loading
        self.refresh(recompose=True)

    def update_statuses(self, statuses: List[Status], prepend: bool = False) -> None:
        """Update the timeline with new statuses.

        Args:
            statuses: List of new statuses
            prepend: Whether to prepend (True) or replace (False) existing statuses
        """
        if prepend:
            # Add new statuses to the beginning
            self._statuses = statuses + self._statuses
        else:
            # Replace all statuses
            self._statuses = statuses

        self._status_widgets.clear()
        self.refresh(recompose=True)

    def append_statuses(self, statuses: List[Status]) -> None:
        """Append statuses to the end of the timeline.

        Args:
            statuses: List of statuses to append
        """
        self._statuses.extend(statuses)

        # Add new status widgets
        for status in statuses:
            status_widget = StatusWidget(status, self.app_ref, media_manager=self.media_manager)
            self._status_widgets.append(status_widget)

        self.refresh(recompose=True)

    def get_statuses(self) -> List[Status]:
        """Get the current list of statuses.

        Returns:
            List of Status objects
        """
        return self._statuses.copy()

    def get_oldest_id(self) -> Optional[str]:
        """Get the ID of the oldest status in the timeline.

        Returns:
            Status ID or None if timeline is empty
        """
        return self._statuses[-1].id if self._statuses else None

    def get_newest_id(self) -> Optional[str]:
        """Get the ID of the newest status in the timeline.

        Returns:
            Status ID or None if timeline is empty
        """
        return self._statuses[0].id if self._statuses else None

    def clear(self) -> None:
        """Clear all statuses from the timeline."""
        self._statuses.clear()
        self._status_widgets.clear()
        self.refresh(recompose=True)

    async def on_status_widget_focus(self, event) -> None:
        """Handle status widget focus events."""
        if isinstance(event.widget, StatusWidget):
            await self.post_message(self.StatusSelected(event.widget.status))

    def action_scroll_to_top(self) -> None:
        """Scroll to the top of the timeline."""
        scroll_view = self.query_one(VerticalScroll)
        scroll_view.scroll_to(y=0, animate=True)

    def action_scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the timeline."""
        scroll_view = self.query_one(VerticalScroll)
        scroll_view.scroll_end(animate=True)

    def action_load_newer(self) -> None:
        """Request loading of newer statuses."""
        self.post_message(self.LoadMore("newer"))

    def action_load_older(self) -> None:
        """Request loading of older statuses."""
        self.post_message(self.LoadMore("older"))


class TimelineWidget(Widget):
    """Container widget for timeline with additional controls."""

    DEFAULT_CSS = """
    TimelineWidget {
        height: 1fr;
        width: 1fr;
    }

    TimelineWidget Timeline {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(
        self,
        statuses: Optional[List[Status]] = None,
        empty_message: str = "No statuses to display",
        load_callback: Optional[
            Callable[[str, Optional[str]], Awaitable[List[Status]]]
        ] = None,
        media_manager: Optional[MediaManager] = None,
        **kwargs
    ):
        """Initialize the timeline widget.

        Args:
            statuses: Initial list of statuses to display
            empty_message: Message to show when timeline is empty
            load_callback: Async callback for loading more statuses
            media_manager: MediaManager instance for handling media previews
        """
        super().__init__(**kwargs)
        self._timeline = Timeline(statuses, empty_message, app_ref=self.app, media_manager=media_manager)
        self._load_callback = load_callback

    def compose(self) -> ComposeResult:
        """Compose the timeline widget layout."""
        yield self._timeline

    async def on_mount(self) -> None:
        """Load initial timeline data when the widget is mounted."""
        if self._load_callback:
            try:
                self._timeline.set_loading(True)
                initial_statuses = await self._load_callback("home", None)
                if initial_statuses:
                    self._timeline.update_statuses(initial_statuses)
                else:
                    # No statuses returned, keep empty message
                    pass
            except Exception:
                # Handle errors gracefully - the empty message will be shown
                self.log.warning("Failed to load timeline data")
            finally:
                self._timeline.set_loading(False)

    async def on_timeline_load_more(self, event: Timeline.LoadMore) -> None:
        """Handle load more requests."""
        if not self._load_callback:
            return

        event.stop()

        try:
            self._timeline.set_loading(True)

            if event.direction == "newer":
                max_id = None
                since_id = self._timeline.get_newest_id()
            else:  # older
                max_id = self._timeline.get_oldest_id()
                since_id = None

            new_statuses = await self._load_callback(
                event.direction, max_id or since_id
            )

            if new_statuses:
                if event.direction == "newer":
                    self._timeline.update_statuses(new_statuses, prepend=True)
                else:
                    self._timeline.append_statuses(new_statuses)

        finally:
            self._timeline.set_loading(False)

    async def on_timeline_status_selected(self, event: Timeline.StatusSelected) -> None:
        """Handle status selection events."""
        # Forward the event up the widget tree
        await self.post_message(event)

    def update_statuses(self, statuses: List[Status], prepend: bool = False) -> None:
        """Update the timeline with new statuses."""
        self._timeline.update_statuses(statuses, prepend)

    def append_statuses(self, statuses: List[Status]) -> None:
        """Append statuses to the timeline."""
        self._timeline.append_statuses(statuses)

    def get_statuses(self) -> List[Status]:
        """Get the current list of statuses."""
        return self._timeline.get_statuses()

    def clear(self) -> None:
        """Clear all statuses from the timeline."""
        self._timeline.clear()

    def set_loading(self, loading: bool) -> None:
        """Set the loading state."""
        self._timeline.set_loading(loading)
