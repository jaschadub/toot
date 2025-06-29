"""Compose widget for creating new toots."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label, Select, TextArea


class ComposeWidget(Widget):
    """Widget for composing new toots."""

    DEFAULT_CSS = """
    ComposeWidget {
        height: auto;
        min-height: 10;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }

    ComposeWidget TextArea {
        height: 6;
        margin-bottom: 1;
    }

    ComposeWidget .compose-header {
        height: 1;
        margin-bottom: 1;
    }

    ComposeWidget .compose-controls {
        height: 1;
        margin-top: 1;
    }

    ComposeWidget .char-counter {
        color: $text-muted;
        text-align: right;
    }

    ComposeWidget .char-counter.warning {
        color: $warning;
    }

    ComposeWidget .char-counter.error {
        color: $error;
    }

    ComposeWidget Button {
        margin-right: 1;
    }

    ComposeWidget Select {
        width: 15;
        margin-right: 1;
    }
    """

    class PostStatus(Message):
        """Message sent when a status should be posted."""

        def __init__(
            self,
            content: str,
            visibility: str = "public",
            in_reply_to_id: Optional[str] = None,
            sensitive: bool = False,
            spoiler_text: Optional[str] = None
        ) -> None:
            self.content = content
            self.visibility = visibility
            self.in_reply_to_id = in_reply_to_id
            self.sensitive = sensitive
            self.spoiler_text = spoiler_text
            super().__init__()

    class Cancel(Message):
        """Message sent when compose is cancelled."""
        pass

    def __init__(
        self,
        reply_to_id: Optional[str] = None,
        initial_content: str = "",
        **kwargs
    ):
        """Initialize the compose widget.

        Args:
            reply_to_id: ID of status being replied to
            initial_content: Initial content for the text area
        """
        super().__init__(**kwargs)
        self.reply_to_id = reply_to_id
        self.initial_content = initial_content
        self.max_chars = 500  # Standard Mastodon limit
        self._text_area: Optional[TextArea] = None
        self._char_counter: Optional[Label] = None
        self._visibility_select: Optional[Select] = None
        self._post_button: Optional[Button] = None

    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        with Vertical():
            # Header
            with Horizontal(classes="compose-header"):
                if self.reply_to_id:
                    yield Label("Reply to toot", classes="compose-title")
                else:
                    yield Label("Compose new toot", classes="compose-title")

                yield Label(
                    f"0/{self.max_chars}",
                    classes="char-counter",
                    id="char-counter"
                )

            # Text area
            yield TextArea(
                text=self.initial_content,
                placeholder="What's on your mind?",
                id="compose-text"
            )

            # Controls
            with Horizontal(classes="compose-controls"):
                # Visibility selector
                yield Select(
                    options=[
                        ("Public", "public"),
                        ("Unlisted", "unlisted"),
                        ("Followers only", "private"),
                        ("Direct message", "direct")
                    ],
                    value="public",
                    id="visibility-select"
                )

                # Action buttons
                yield Button("Cancel", variant="default", id="cancel-button")
                yield Button("Post", variant="primary", id="post-button")

    def on_mount(self) -> None:
        """Handle widget mounting."""
        self._text_area = self.query_one("#compose-text", TextArea)
        self._char_counter = self.query_one("#char-counter", Label)
        self._visibility_select = self.query_one("#visibility-select", Select)
        self._post_button = self.query_one("#post-button", Button)

        # Focus the text area
        self._text_area.focus()

        # Update character counter
        self._update_char_counter()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area content changes."""
        if event.text_area.id == "compose-text":
            self._update_char_counter()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "post-button":
            self._post_status()
        elif event.button.id == "cancel-button":
            self.post_message(self.Cancel())

    def _update_char_counter(self) -> None:
        """Update the character counter display."""
        if not self._text_area or not self._char_counter:
            return

        content = self._text_area.text
        char_count = len(content)
        remaining = self.max_chars - char_count

        # Update counter text
        self._char_counter.update(f"{char_count}/{self.max_chars}")

        # Update counter styling
        self._char_counter.remove_class("warning", "error")
        if remaining < 0:
            self._char_counter.add_class("error")
            if self._post_button:
                self._post_button.disabled = True
        elif remaining < 50:
            self._char_counter.add_class("warning")
            if self._post_button:
                self._post_button.disabled = False
        else:
            if self._post_button:
                self._post_button.disabled = char_count == 0

    def _post_status(self) -> None:
        """Post the composed status."""
        if not self._text_area or not self._visibility_select:
            return

        content = self._text_area.text.strip()
        if not content:
            return

        visibility = self._visibility_select.value

        self.post_message(self.PostStatus(
            content=content,
            visibility=visibility,
            in_reply_to_id=self.reply_to_id
        ))

    def clear(self) -> None:
        """Clear the compose widget."""
        if self._text_area:
            self._text_area.text = ""
        if self._visibility_select:
            self._visibility_select.value = "public"
        self._update_char_counter()

    def set_content(self, content: str) -> None:
        """Set the content of the text area.

        Args:
            content: Content to set
        """
        if self._text_area:
            self._text_area.text = content
            self._update_char_counter()

    def get_content(self) -> str:
        """Get the current content of the text area.

        Returns:
            Current text content
        """
        return self._text_area.text if self._text_area else ""

    def set_visibility(self, visibility: str) -> None:
        """Set the visibility setting.

        Args:
            visibility: Visibility level (public, unlisted, private, direct)
        """
        if self._visibility_select:
            self._visibility_select.value = visibility

    def get_visibility(self) -> str:
        """Get the current visibility setting.

        Returns:
            Current visibility level
        """
        return self._visibility_select.value if self._visibility_select else "public"
