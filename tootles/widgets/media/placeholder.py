"""Placeholder widgets for media loading states and errors."""

from textual.widget import Widget
from textual.widgets import Static


class MediaPlaceholderWidget(Widget):
    """Base placeholder widget for media."""

    DEFAULT_CSS = """
    MediaPlaceholderWidget {
        height: auto;
        min-height: 3;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    .placeholder-loading {
        color: $warning;
    }

    .placeholder-error {
        color: $error;
    }

    .placeholder-disabled {
        color: $text-muted;
    }

    .placeholder-unsupported {
        color: $text-muted;
    }
    """

    def __init__(self, message: str, placeholder_type: str = "default", **kwargs):
        """Initialize placeholder widget.

        Args:
            message: Message to display
            placeholder_type: Type of placeholder ("loading", "error", "disabled", "unsupported")
            **kwargs: Additional widget arguments
        """
        super().__init__(**kwargs)
        self.message = message
        self.placeholder_type = placeholder_type

    def compose(self):
        """Compose the placeholder widget."""
        css_class = f"placeholder-{self.placeholder_type}"
        yield Static(self.message, classes=css_class)


class LoadingPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown while media is loading."""

    def __init__(self, **kwargs):
        super().__init__("⏳ Loading media...", "loading", **kwargs)


class ErrorPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown when media loading fails."""

    def __init__(self, error_message: str = "Failed to load media", **kwargs):
        super().__init__(f"❌ {error_message}", "error", **kwargs)


class DisabledPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown when media previews are disabled."""

    def __init__(self, attachment, **kwargs):
        message = f"📎 {attachment.description or 'Media attachment'} (previews disabled)"
        super().__init__(message, "disabled", **kwargs)


class UnsupportedPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown for unsupported media types."""

    def __init__(self, attachment, **kwargs):
        message = f"❓ {attachment.description or 'Unsupported media type'}"
        super().__init__(message, "unsupported", **kwargs)


class NetworkErrorPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown when network loading fails."""

    def __init__(self, **kwargs):
        super().__init__("🌐 Network error - Press 'r' to retry", "error", **kwargs)


class TimeoutPlaceholder(MediaPlaceholderWidget):
    """Placeholder shown when media loading times out."""

    def __init__(self, **kwargs):
        super().__init__("⏰ Loading timed out - Press 'r' to retry", "error", **kwargs)
