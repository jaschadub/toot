"""Compose screen for creating new toots."""

from typing import TYPE_CHECKING, Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, TextArea

if TYPE_CHECKING:
    from tootles.api.models import Status
    from tootles.main import TootlesApp


class ComposeWidget(ModalScreen):
    """Modal screen for composing new toots."""

    DEFAULT_CSS = """
    ComposeWidget {
        align: center middle;
    }

    ComposeWidget > Vertical {
        width: 80;
        height: 25;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    ComposeWidget TextArea {
        height: 10;
        margin-bottom: 1;
    }

    ComposeWidget .compose-header {
        height: 3;
        margin-bottom: 1;
    }

    ComposeWidget .compose-controls {
        height: 3;
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

    ComposeWidget .reply-info {
        color: $text-muted;
        margin-bottom: 1;
        padding: 1;
        border: solid $border;
        background: $surface-lighten-1;
    }
    """

    def __init__(
        self,
        app_ref: "TootlesApp",
        reply_to: Optional["Status"] = None,
        initial_content: str = "",
        **kwargs
    ):
        """Initialize the compose screen.

        Args:
            app_ref: Reference to the main application
            reply_to: Status being replied to
            initial_content: Initial content for the text area
        """
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.reply_to = reply_to
        self.initial_content = initial_content
        self.max_chars = 500  # Standard Mastodon limit

        # Set initial content for replies
        if reply_to and not initial_content:
            self.initial_content = f"@{reply_to.account.acct} "

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        with Vertical():
            # Header
            with Horizontal(classes="compose-header"):
                if self.reply_to:
                    yield Label("Reply to toot", classes="compose-title")
                else:
                    yield Label("Compose new toot", classes="compose-title")

                yield Label(
                    f"0/{self.max_chars}",
                    classes="char-counter",
                    id="char-counter"
                )

            # Reply info if replying
            if self.reply_to:
                reply_text = (
                    self.reply_to.content[:100] + "..."
                    if len(self.reply_to.content) > 100
                    else self.reply_to.content
                )
                yield Label(
                    f"Replying to @{self.reply_to.account.acct}: {reply_text}",
                    classes="reply-info"
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

    async def on_mount(self) -> None:
        """Handle screen mounting."""
        # Focus the text area
        text_area = self.query_one("#compose-text", TextArea)
        text_area.focus()

        # Update character counter
        self._update_char_counter()

    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area content changes."""
        if event.text_area.id == "compose-text":
            self._update_char_counter()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "post-button":
            await self._post_status()
        elif event.button.id == "cancel-button":
            self.app.pop_screen()

    def _update_char_counter(self) -> None:
        """Update the character counter display."""
        try:
            text_area = self.query_one("#compose-text", TextArea)
            char_counter = self.query_one("#char-counter", Label)
            post_button = self.query_one("#post-button", Button)

            content = text_area.text
            char_count = len(content)
            remaining = self.max_chars - char_count

            # Update counter text
            char_counter.update(f"{char_count}/{self.max_chars}")

            # Update counter styling
            char_counter.remove_class("warning", "error")
            if remaining < 0:
                char_counter.add_class("error")
                post_button.disabled = True
            elif remaining < 50:
                char_counter.add_class("warning")
                post_button.disabled = False
            else:
                post_button.disabled = char_count == 0

        except Exception:
            # Widgets might not be mounted yet during initialization
            return

    async def _post_status(self) -> None:
        """Post the composed status."""
        try:
            text_area = self.query_one("#compose-text", TextArea)
            visibility_select = self.query_one("#visibility-select", Select)

            content = text_area.text.strip()
            if not content:
                self.app.notify("Cannot post empty status", severity="warning")
                return

            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            visibility = visibility_select.value
            in_reply_to_id = self.reply_to.id if self.reply_to else None

            # Post the status
            await self.app_ref.api_client.post_status(
                content=content,
                visibility=visibility,
                in_reply_to_id=in_reply_to_id
            )

            self.app.notify("Status posted successfully!", severity="success")
            self.app.pop_screen()

        except Exception as e:
            self.app.notify(f"Failed to post status: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel compose (Escape key)."""
        self.app.pop_screen()
