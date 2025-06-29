"""Status widget for displaying individual toots."""

from datetime import datetime

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label, Static

from ..api.models import Status


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
        height: 1;
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
    """

    def __init__(self, status: Status, **kwargs):
        """Initialize the status widget.

        Args:
            status: The Status object to display
        """
        super().__init__(**kwargs)
        self.status = status
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

            # Status footer with stats
            with Horizontal(classes="status-footer"):
                yield Label(
                    f"💬 {display_status.replies_count}",
                    classes="stats"
                )
                yield Label(
                    f"🔄 {display_status.reblogs_count}",
                    classes="stats"
                )
                yield Label(
                    f"⭐ {display_status.favourites_count}",
                    classes="stats"
                )

                # Interaction indicators
                indicators = []
                if display_status.favourited:
                    indicators.append("⭐")
                if display_status.reblogged:
                    indicators.append("🔄")
                if display_status.bookmarked:
                    indicators.append("🔖")

                if indicators:
                    yield Label(
                        " ".join(indicators),
                        classes="stats"
                    )

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

        # Add media indicator
        if status.media_attachments:
            media_count = len(status.media_attachments)
            media_types = {m.type for m in status.media_attachments}

            if "image" in media_types:
                content.append(f"\n📷 {media_count} image(s)", style="dim")
            elif "video" in media_types:
                content.append(f"\n🎥 {media_count} video(s)", style="dim")
            elif "audio" in media_types:
                content.append(f"\n🎵 {media_count} audio file(s)", style="dim")
            else:
                content.append(f"\n📎 {media_count} attachment(s)", style="dim")

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
        # This will be implemented when we add action handling
        pass

    def action_toggle_reblog(self) -> None:
        """Toggle reblog status of this toot."""
        # This will be implemented when we add action handling
        pass

    def action_reply(self) -> None:
        """Reply to this toot."""
        # This will be implemented when we add action handling
        pass

    def action_bookmark(self) -> None:
        """Toggle bookmark status of this toot."""
        # This will be implemented when we add action handling
        pass
