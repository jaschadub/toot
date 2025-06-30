"""Individual media widget for displaying single media attachments."""

import asyncio
import logging
from typing import Optional

from textual import events
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from ...media.formats import MediaFormat, get_media_format

logger = logging.getLogger(__name__)


class MediaWidget(Widget):
    """Widget for displaying individual media attachments."""

    DEFAULT_CSS = """
    MediaWidget {
        height: auto;
        min-height: 3;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    MediaWidget:focus {
        border: solid $accent;
    }

    MediaWidget.loading {
        border: solid $warning;
    }

    MediaWidget.error {
        border: solid $error;
    }

    .media-image-preview {
        color: $text;
    }

    .media-image-placeholder {
        color: $text-muted;
    }

    .media-video-placeholder {
        color: $primary;
    }

    .media-audio-placeholder {
        color: $secondary;
    }

    .media-generic-placeholder {
        color: $text-muted;
    }
    """

    can_focus = True
    loading = reactive(False)

    class MediaActivated(Message):
        """Message sent when media is activated (Enter pressed)."""

        def __init__(self, widget: "MediaWidget", attachment) -> None:
            self.widget = widget
            self.attachment = attachment
            super().__init__()

    def __init__(
        self,
        attachment,
        media_manager,
        size: str = "thumbnail",
        **kwargs
    ):
        """Initialize media widget.

        Args:
            attachment: MediaAttachment object
            media_manager: MediaManager instance
            size: Size hint ("thumbnail", "medium", "full")
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.attachment = attachment
        self.media_manager = media_manager
        self.size = size
        self._content_widget: Optional[Widget] = None
        self._load_task: Optional[asyncio.Task] = None

    def compose(self):
        """Compose the widget."""
        # Start with loading placeholder
        self.loading = True
        yield Static("⏳ Loading media...", classes="loading-placeholder")

    async def on_mount(self) -> None:
        """Handle widget mounting."""
        # Start loading media content
        self._load_task = asyncio.create_task(self._load_media_content())

    async def _load_media_content(self) -> None:
        """Load and display media content."""
        try:
            # Get media widget from manager
            content_widget = await self.media_manager.get_media_widget(
                self.attachment,
                self.size,
                preload=True
            )

            # Replace loading placeholder with actual content
            await self._replace_content(content_widget)
            self.loading = False

        except Exception as e:
            logger.error(f"Failed to load media content: {e}")
            await self._show_error("Failed to load media")
            self.loading = False

    async def _replace_content(self, new_widget: Widget) -> None:
        """Replace current content with new widget.

        Args:
            new_widget: New widget to display
        """
        # Remove existing content
        if self._content_widget:
            await self._content_widget.remove()

        # Add new content
        await self.mount(new_widget)
        self._content_widget = new_widget

        # Remove loading placeholder
        loading_placeholder = self.query_one(".loading-placeholder", Static)
        await loading_placeholder.remove()

    async def _show_error(self, error_message: str) -> None:
        """Show error message.

        Args:
            error_message: Error message to display
        """
        error_widget = Static(f"❌ {error_message}", classes="error-placeholder")
        await self._replace_content(error_widget)
        self.add_class("error")

    async def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "enter":
            # Activate media (open externally or fullscreen)
            self.post_message(self.MediaActivated(self, self.attachment))
            event.prevent_default()
        elif event.key == "r":
            # Reload media
            await self._reload_media()
            event.prevent_default()

    async def _reload_media(self) -> None:
        """Reload media content."""
        if self._load_task and not self._load_task.done():
            self._load_task.cancel()

        self.loading = True
        self.remove_class("error")

        # Show loading placeholder
        loading_widget = Static("⏳ Reloading media...", classes="loading-placeholder")
        if self._content_widget:
            await self._content_widget.remove()
        await self.mount(loading_widget)

        # Start loading again
        self._load_task = asyncio.create_task(self._load_media_content())

    def get_media_format(self) -> MediaFormat:
        """Get media format for this attachment.

        Returns:
            MediaFormat enum value
        """
        return get_media_format(self.attachment.url, self.attachment.type)

    def can_display_inline(self) -> bool:
        """Check if this media can be displayed inline.

        Returns:
            True if can display inline
        """
        return self.media_manager.can_display_inline(self.attachment)

    def is_external_viewer_available(self) -> bool:
        """Check if external viewer is available.

        Returns:
            True if external viewer is available
        """
        return self.media_manager.is_external_viewer_available(self.attachment)

    async def open_external(self) -> bool:
        """Open media in external viewer.

        Returns:
            True if successfully opened
        """
        try:
            return await self.media_manager.open_media_external(self.attachment)
        except Exception as e:
            logger.error(f"Failed to open media externally: {e}")
            return False

    def __del__(self):
        """Cleanup on destruction."""
        if self._load_task and not self._load_task.done():
            self._load_task.cancel()
