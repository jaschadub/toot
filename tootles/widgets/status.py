"""Status widget for displaying individual toots."""

from datetime import datetime
from typing import TYPE_CHECKING

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Label, Static

from ..api.models import Status
from ..media.manager import MediaManager
from ..widgets.media import MediaGalleryWidget, MediaWidget

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class StatusWidget(Widget):
    """Widget for displaying a single status/toot."""

    DEFAULT_CSS = """
    StatusWidget {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $surface;
        background: $surface;
    }

    StatusWidget:focus {
        border: solid $accent;
    }

    StatusWidget .status-header {
        height: 1;
        margin-bottom: 1;
    }

    StatusWidget .status-content {
        height: auto;
        margin-bottom: 1;
    }

    StatusWidget .status-footer {
        height: 3;
    }

    StatusWidget .username {
        color: $primary;
        text-style: bold;
    }

    StatusWidget .handle {
        color: $text-muted;
    }

    StatusWidget .timestamp {
        color: $text-muted;
        text-align: right;
    }

    StatusWidget .stats {
        color: $text-muted;
    }

    StatusWidget .reblog-indicator {
        color: $success;
        text-style: italic;
    }

    StatusWidget .action-buttons {
        height: 3;
    }

    StatusWidget .action-buttons Button {
        margin-right: 1;
        min-width: 8;
    }

    StatusWidget .media-text-indicator {
        color: $text-muted;
        text-style: italic;
        margin: 1 0;
    }
    """

    def __init__(self, status: Status, app_ref: "TootlesApp", media_manager: MediaManager = None, **kwargs):
        """Initialize the status widget.

        Args:
            status: The Status object to display
            app_ref: Reference to the main application
            media_manager: MediaManager instance for handling media previews
        """
        super().__init__(**kwargs)
        self.status = status
        self.app_ref = app_ref
        self.media_manager = media_manager or getattr(app_ref, 'media_manager', None)
        self.can_focus = True

    def compose(self) -> ComposeResult:
        """Compose the status widget layout."""
        # Handle reblogs
        display_status = self.status.reblog if self.status.reblog else self.status

        with Vertical():
            # Reblog indicator if this is a reblog
            if self.status.reblog:
                yield Static(
                    f"🔄 {escape(self.status.account.display_name)} reblogged",
                    classes="reblog-indicator"
                )

            # Status header with user info and timestamp
            with Horizontal(classes="status-header"):
                yield Label(
                    escape(display_status.account.display_name),
                    classes="username"
                )
                yield Label(
                    f"@{escape(display_status.account.acct)}",
                    classes="handle"
                )
                yield Label(
                    self._format_timestamp(display_status.created_at),
                    classes="timestamp"
                )

            # Status content
            yield Static(
                self._format_content(display_status),
                classes="status-content"
            )

            # Media attachments - use new media system
            if display_status.media_attachments:
                yield from self._create_media_widgets(display_status.media_attachments)

            # Action buttons
            with Horizontal(classes="action-buttons"):
                yield Button(
                    "💬 Reply",
                    id="reply-btn",
                    variant="default"
                )

                reblog_variant = "success" if display_status.reblogged else "default"
                yield Button(
                    f"🔁 {display_status.reblogs_count}",
                    id="reblog-btn",
                    variant=reblog_variant
                )

                favorite_variant = "warning" if display_status.favourited else "default"
                yield Button(
                    f"⭐ {display_status.favourites_count}",
                    id="favorite-btn",
                    variant=favorite_variant
                )

                bookmark_variant = "primary" if display_status.bookmarked else "default"
                yield Button(
                    "🔖 Bookmark",
                    id="bookmark-btn",
                    variant=bookmark_variant
                )

    def _create_media_widgets(self, media_attachments):
        """Create appropriate media widgets based on configuration and attachments.

        Args:
            media_attachments: List of media attachment objects

        Yields:
            Media widgets or text indicators
        """
        if not self.media_manager:
            # Fallback to text indicators when no media manager
            yield from self._create_text_indicators(media_attachments)
            return

        # Check if media previews are enabled
        config = getattr(self.app_ref, 'config', None)
        if config and hasattr(config, 'media') and not config.media.show_media_previews:
            # Media previews disabled - use text indicators
            yield from self._create_text_indicators(media_attachments)
            return
        elif config and hasattr(config, 'show_media_previews') and not config.show_media_previews:
            # Legacy config check
            yield from self._create_text_indicators(media_attachments)
            return

        try:
            # Use new media system
            if len(media_attachments) == 1:
                # Single media item - use individual MediaWidget
                yield MediaWidget(
                    media_attachments[0],
                    self.media_manager,
                    size="thumbnail"
                )
            else:
                # Multiple media items - use MediaGalleryWidget
                yield MediaGalleryWidget(
                    media_attachments,
                    self.media_manager
                )
        except Exception:
            # Graceful fallback to text indicators on any error
            yield from self._create_text_indicators(media_attachments)

    def _create_text_indicators(self, media_attachments):
        """Create text-based media indicators as fallback.

        Args:
            media_attachments: List of media attachment objects

        Yields:
            Static widgets with text indicators
        """
        for attachment in media_attachments:
            media_type = getattr(attachment, 'type', 'unknown')
            description = getattr(attachment, 'description', None)

            if media_type == 'image':
                icon = "🖼️"
                type_text = "Image"
            elif media_type == 'video':
                icon = "🎥"
                type_text = "Video"
            elif media_type == 'audio':
                icon = "🎵"
                type_text = "Audio"
            elif media_type == 'gifv':
                icon = "🎞️"
                type_text = "GIF"
            else:
                icon = "📎"
                type_text = "Media"

            if description:
                text = f"{icon} {type_text}: {description}"
            else:
                text = f"{icon} {type_text} attachment"

            yield Static(text, classes="media-text-indicator")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "reply-btn":
            await self.handle_reply()
        elif event.button.id == "reblog-btn":
            await self.handle_reblog()
        elif event.button.id == "favorite-btn":
            await self.handle_favorite()
        elif event.button.id == "bookmark-btn":
            await self.handle_bookmark()

    async def handle_reply(self) -> None:
        """Handle reply to status."""
        try:
            from tootles.widgets.compose import ComposeWidget
            compose_widget = ComposeWidget(self.app_ref, reply_to=self.status)
            self.app.push_screen(compose_widget)
        except Exception as e:
            self.app.notify(f"Failed to open reply: {e}", severity="error")

    async def handle_reblog(self) -> None:
        """Handle reblog/boost of status."""
        try:
            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            display_status = self.status.reblog if self.status.reblog else self.status

            if display_status.reblogged:
                await self.app_ref.api_client.unreblog_status(display_status.id)
                display_status.reblogged = False
                display_status.reblogs_count -= 1
                self.app.notify("Unboosted", severity="success")
            else:
                await self.app_ref.api_client.reblog_status(display_status.id)
                display_status.reblogged = True
                display_status.reblogs_count += 1
                self.app.notify("Boosted!", severity="success")

            # Update button appearance
            self.update_action_buttons()

        except Exception as e:
            self.app.notify(f"Failed to reblog: {e}", severity="error")

    async def handle_favorite(self) -> None:
        """Handle favorite/unfavorite of status."""
        try:
            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            display_status = self.status.reblog if self.status.reblog else self.status

            if display_status.favourited:
                await self.app_ref.api_client.unfavourite_status(display_status.id)
                display_status.favourited = False
                display_status.favourites_count -= 1
                self.app.notify("Unfavorited", severity="success")
            else:
                await self.app_ref.api_client.favourite_status(display_status.id)
                display_status.favourited = True
                display_status.favourites_count += 1
                self.app.notify("Favorited!", severity="success")

            # Update button appearance
            self.update_action_buttons()

        except Exception as e:
            self.app.notify(f"Failed to favorite: {e}", severity="error")

    async def handle_bookmark(self) -> None:
        """Handle bookmark/unbookmark of status."""
        try:
            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            display_status = self.status.reblog if self.status.reblog else self.status

            if display_status.bookmarked:
                await self.app_ref.api_client.unbookmark_status(display_status.id)
                display_status.bookmarked = False
                self.app.notify("Bookmark removed", severity="success")
            else:
                await self.app_ref.api_client.bookmark_status(display_status.id)
                display_status.bookmarked = True
                self.app.notify("Bookmarked!", severity="success")

            # Update button appearance
            self.update_action_buttons()

        except Exception as e:
            self.app.notify(f"Failed to bookmark: {e}", severity="error")

    def update_action_buttons(self) -> None:
        """Update action button appearance based on status state."""
        try:
            display_status = self.status.reblog if self.status.reblog else self.status

            reblog_btn = self.query_one("#reblog-btn", Button)
            favorite_btn = self.query_one("#favorite-btn", Button)
            bookmark_btn = self.query_one("#bookmark-btn", Button)

            # Update reblog button
            if display_status.reblogged:
                reblog_btn.variant = "success"
            else:
                reblog_btn.variant = "default"
            reblog_btn.label = f"🔁 {display_status.reblogs_count}"

            # Update favorite button
            if display_status.favourited:
                favorite_btn.variant = "warning"
            else:
                favorite_btn.variant = "default"
            favorite_btn.label = f"⭐ {display_status.favourites_count}"

            # Update bookmark button
            if display_status.bookmarked:
                bookmark_btn.variant = "primary"
            else:
                bookmark_btn.variant = "default"

        except Exception:
            # Buttons might not be mounted yet during initialization
            return

    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display.

        Args:
            timestamp: The datetime to format

        Returns:
            Formatted timestamp string
        """
        now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days}d"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m"
        else:
            return "now"

    def _format_content(self, status: Status) -> Text:
        """Format status content for display.

        Args:
            status: The Status object

        Returns:
            Rich Text object with formatted content
        """
        content = Text()

        # Add spoiler text if present
        if status.spoiler_text:
            content.append(f"⚠️  {status.spoiler_text}\n", style="bold yellow")
            if status.sensitive:
                content.append("[Click to show content]\n", style="dim")
                return content

        # Strip HTML tags and decode entities (basic implementation)
        text_content = self._strip_html(status.content)

        # Add content
        content.append(text_content)

        # Add poll indicator
        if status.poll:
            content.append("\n📊 Poll", style="dim")

        return content

    def _strip_html(self, html_content: str) -> str:
        """Basic HTML tag stripping and entity decoding.

        Args:
            html_content: HTML content to clean

        Returns:
            Plain text content
        """
        import re

        # Replace common HTML entities
        html_content = html_content.replace("&lt;", "<")
        html_content = html_content.replace("&gt;", ">")
        html_content = html_content.replace("&amp;", "&")
        html_content = html_content.replace("&quot;", '"')
        html_content = html_content.replace("&#39;", "'")

        # Replace <br> tags with newlines
        html_content = re.sub(r"<br\s*/?>", "\n", html_content, flags=re.IGNORECASE)

        # Replace paragraph tags with double newlines
        html_content = re.sub(r"</p>\s*<p>", "\n\n", html_content, flags=re.IGNORECASE)
        html_content = re.sub(r"</?p>", "", html_content, flags=re.IGNORECASE)

        # Remove all other HTML tags
        html_content = re.sub(r"<[^>]+>", "", html_content)

        # Clean up extra whitespace
        html_content = re.sub(r"\n\s*\n", "\n\n", html_content)
        html_content = html_content.strip()

        return html_content

    def action_toggle_favourite(self) -> None:
        """Toggle favourite status of this toot."""
        self.run_worker(self.handle_favorite())

    def action_toggle_reblog(self) -> None:
        """Toggle reblog status of this toot."""
        self.run_worker(self.handle_reblog())

    def action_reply(self) -> None:
        """Reply to this toot."""
        self.run_worker(self.handle_reply())

    def action_bookmark(self) -> None:
        """Toggle bookmark status of this toot."""
        self.run_worker(self.handle_bookmark())
