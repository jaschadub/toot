"""Media gallery widget for displaying multiple media attachments."""

import asyncio
import logging
from typing import List, Optional

from textual import events
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from .widget import MediaWidget

logger = logging.getLogger(__name__)


class MediaGalleryWidget(Widget):
    """Widget for displaying multiple media attachments in a gallery layout."""

    DEFAULT_CSS = """
    MediaGalleryWidget {
        height: auto;
        min-height: 5;
        margin: 1 0;
    }

    MediaGalleryWidget Horizontal {
        height: auto;
        align: left middle;
    }

    MediaGalleryWidget Vertical {
        height: auto;
    }

    .media-gallery-header {
        color: $text-muted;
        margin-bottom: 1;
    }

    .media-gallery-single {
        width: 100%;
    }

    .media-gallery-grid {
        width: 50%;
    }

    .media-gallery-list {
        width: 100%;
        margin-bottom: 1;
    }
    """

    can_focus = True
    current_index = reactive(0)

    class MediaSelected(Message):
        """Message sent when a media item is selected."""

        def __init__(self, widget: "MediaGalleryWidget", attachment, index: int) -> None:
            self.widget = widget
            self.attachment = attachment
            self.index = index
            super().__init__()

    def __init__(
        self,
        attachments: List,
        media_manager,
        layout: str = "auto",
        size: str = "thumbnail",
        **kwargs
    ):
        """Initialize media gallery widget.

        Args:
            attachments: List of MediaAttachment objects
            media_manager: MediaManager instance
            layout: Layout style ("auto", "grid", "list", "single")
            size: Size hint for media widgets
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.attachments = attachments
        self.media_manager = media_manager
        self.layout_style = layout
        self.size = size
        self.media_widgets: List[MediaWidget] = []
        self._preload_task: Optional[asyncio.Task] = None

    def compose(self):
        """Compose the widget."""
        if not self.attachments:
            yield Static("No media attachments", classes="media-gallery-empty")
            return

        # Determine layout based on number of attachments
        actual_layout = self._determine_layout()

        # Create header
        count = len(self.attachments)
        header_text = f"📎 {count} media attachment{'s' if count > 1 else ''}"
        yield Static(header_text, classes="media-gallery-header")

        # Create media widgets based on layout
        if actual_layout == "single":
            yield from self._create_single_layout()
        elif actual_layout == "grid":
            yield from self._create_grid_layout()
        elif actual_layout == "list":
            yield from self._create_list_layout()

    def _determine_layout(self) -> str:
        """Determine the actual layout to use.

        Returns:
            Layout style to use
        """
        if self.layout_style != "auto":
            return self.layout_style

        count = len(self.attachments)
        if count == 1:
            return "single"
        elif count <= 4:
            return "grid"
        else:
            return "list"

    def _create_single_layout(self):
        """Create single media layout."""
        if self.attachments:
            widget = MediaWidget(
                self.attachments[0],
                self.media_manager,
                self.size,
                classes="media-gallery-single"
            )
            self.media_widgets.append(widget)
            yield widget

    def _create_grid_layout(self):
        """Create grid layout for multiple media."""
        # Create rows of media widgets
        for i in range(0, len(self.attachments), 2):
            row_attachments = self.attachments[i:i+2]

            if len(row_attachments) == 1:
                # Single item in row
                widget = MediaWidget(
                    row_attachments[0],
                    self.media_manager,
                    self.size,
                    classes="media-gallery-single"
                )
                self.media_widgets.append(widget)
                yield widget
            else:
                # Two items in row
                row_widgets = []
                for attachment in row_attachments:
                    widget = MediaWidget(
                        attachment,
                        self.media_manager,
                        self.size,
                        classes="media-gallery-grid"
                    )
                    self.media_widgets.append(widget)
                    row_widgets.append(widget)

                yield Horizontal(*row_widgets)

    def _create_list_layout(self):
        """Create list layout for many media."""
        container_widgets = []
        for attachment in self.attachments:
            widget = MediaWidget(
                attachment,
                self.media_manager,
                self.size,
                classes="media-gallery-list"
            )
            self.media_widgets.append(widget)
            container_widgets.append(widget)

        yield Vertical(*container_widgets)

    async def on_mount(self) -> None:
        """Handle widget mounting."""
        # Set up message handlers for media widgets
        for i, widget in enumerate(self.media_widgets):
            widget.index = i

        # Start preloading media
        self._preload_task = asyncio.create_task(self._preload_media())

    async def _preload_media(self) -> None:
        """Preload media for better performance."""
        try:
            await self.media_manager.preload_media(self.attachments)
        except Exception as e:
            logger.debug(f"Failed to preload gallery media: {e}")

    async def on_media_widget_media_activated(self, message: MediaWidget.MediaActivated) -> None:
        """Handle media widget activation."""
        # Find the index of the activated widget
        try:
            index = self.media_widgets.index(message.widget)
            self.current_index = index

            # Post selection message
            self.post_message(self.MediaSelected(self, message.attachment, index))
        except ValueError:
            logger.warning("Could not find activated media widget in gallery")

    async def on_key(self, event: events.Key) -> None:
        """Handle key events for gallery navigation."""
        if event.key == "left" and self.current_index > 0:
            await self._navigate_to(self.current_index - 1)
            event.prevent_default()
        elif event.key == "right" and self.current_index < len(self.media_widgets) - 1:
            await self._navigate_to(self.current_index + 1)
            event.prevent_default()
        elif event.key == "home":
            await self._navigate_to(0)
            event.prevent_default()
        elif event.key == "end":
            await self._navigate_to(len(self.media_widgets) - 1)
            event.prevent_default()
        elif event.key == "enter":
            # Activate current media
            if 0 <= self.current_index < len(self.media_widgets):
                self.post_message(self.MediaSelected(
                    self,
                    self.attachments[self.current_index],
                    self.current_index
                ))
            event.prevent_default()

    async def _navigate_to(self, index: int) -> None:
        """Navigate to specific media index.

        Args:
            index: Index to navigate to
        """
        if 0 <= index < len(self.media_widgets):
            # Remove focus from current widget
            if 0 <= self.current_index < len(self.media_widgets):
                self.media_widgets[self.current_index].can_focus = False

            # Set focus to new widget
            self.current_index = index
            self.media_widgets[index].can_focus = True
            self.media_widgets[index].focus()

    async def open_current_external(self) -> bool:
        """Open currently selected media in external viewer.

        Returns:
            True if successfully opened
        """
        if 0 <= self.current_index < len(self.media_widgets):
            return await self.media_widgets[self.current_index].open_external()
        return False

    def get_current_attachment(self):
        """Get currently selected attachment.

        Returns:
            Current MediaAttachment or None
        """
        if 0 <= self.current_index < len(self.attachments):
            return self.attachments[self.current_index]
        return None

    def get_attachment_count(self) -> int:
        """Get number of attachments in gallery.

        Returns:
            Number of attachments
        """
        return len(self.attachments)

    def __del__(self):
        """Cleanup on destruction."""
        if self._preload_task and not self._preload_task.done():
            self._preload_task.cancel()
