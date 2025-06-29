"""Help screen for Tootles with keyboard shortcuts and usage information."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, Static

from tootles.screens.base import BaseScreen

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class HelpScreen(BaseScreen):
    """Help screen showing keyboard shortcuts and usage information."""

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Help"

    def compose(self) -> ComposeResult:
        """Create the help screen layout."""
        with VerticalScroll():
            yield Static("Tootles Help", classes="help-title")

            # Keyboard Shortcuts
            with Vertical(classes="help-section"):
                yield Label("Keyboard Shortcuts", classes="section-title")

                shortcuts = [
                    ("Ctrl+Q", "Quit application"),
                    ("Ctrl+P", "Open command palette"),
                    ("Ctrl+R", "Refresh current timeline"),
                    ("Ctrl+T", "Toggle theme"),
                    ("H", "Go to home timeline"),
                    ("N", "Go to notifications"),
                    ("E", "Go to explore"),
                    ("B", "Go to bookmarks"),
                    ("F", "Go to favorites"),
                    ("L", "Go to lists"),
                    ("C", "Compose new post"),
                    ("S", "Go to settings"),
                    ("?", "Show this help screen"),
                    ("Escape", "Go back/close modal"),
                ]

                for key, description in shortcuts:
                    with Horizontal(classes="shortcut-row"):
                        yield Label(key, classes="shortcut-key")
                        yield Label(description, classes="shortcut-desc")

            # Timeline Navigation
            with Vertical(classes="help-section"):
                yield Label("Timeline Navigation", classes="section-title")

                timeline_shortcuts = [
                    ("↑/↓", "Navigate between posts"),
                    ("J/K", "Navigate between posts (vim-style)"),
                    ("Enter", "Open post details"),
                    ("R", "Reply to post"),
                    ("T", "Reblog/boost post"),
                    ("F", "Favorite post"),
                    ("M", "Bookmark post"),
                    ("D", "Delete post (if yours)"),
                    ("Home", "Go to top of timeline"),
                    ("End", "Go to bottom of timeline"),
                    ("Page Up/Down", "Scroll timeline"),
                ]

                for key, description in timeline_shortcuts:
                    with Horizontal(classes="shortcut-row"):
                        yield Label(key, classes="shortcut-key")
                        yield Label(description, classes="shortcut-desc")

            # Compose Shortcuts
            with Vertical(classes="help-section"):
                yield Label("Compose Shortcuts", classes="section-title")

                compose_shortcuts = [
                    ("Ctrl+Enter", "Send post"),
                    ("Ctrl+D", "Add content warning"),
                    ("Ctrl+M", "Change visibility"),
                    ("Ctrl+A", "Attach media"),
                    ("Escape", "Cancel compose"),
                    ("Tab", "Navigate between fields"),
                ]

                for key, description in compose_shortcuts:
                    with Horizontal(classes="shortcut-row"):
                        yield Label(key, classes="shortcut-key")
                        yield Label(description, classes="shortcut-desc")

            # Getting Started
            with Vertical(classes="help-section"):
                yield Label("Getting Started", classes="section-title")
                yield Static(
                    "1. Configure your Mastodon instance in Settings (S)\n"
                    "2. Enter your instance URL (e.g., mastodon.social)\n"
                    "3. Generate an access token from your instance's settings\n"
                    "4. Paste the token in the Access Token field\n"
                    "5. Save settings and restart Tootles\n"
                    "6. Navigate timelines with H, N, E keys\n"
                    "7. Compose posts with C key",
                    classes="help-text"
                )

            # Theming
            with Vertical(classes="help-section"):
                yield Label("Custom Themes", classes="section-title")
                yield Static(
                    "Tootles supports custom CSS themes:\n\n"
                    "1. Go to Settings and export a theme template\n"
                    "2. Edit the CSS file in ~/.config/tootles/themes/\n"
                    "3. Customize colors and styles to your liking\n"
                    "4. Select your theme in Settings\n"
                    "5. Enable hot-reload for live editing\n\n"
                    "Built-in themes: Default, Dark, Light, High Contrast",
                    classes="help-text"
                )

            # Troubleshooting
            with Vertical(classes="help-section"):
                yield Label("Troubleshooting", classes="section-title")
                yield Static(
                    "Common issues and solutions:\n\n"
                    "• Can't connect: Check instance URL and access token\n"
                    "• Timeline not loading: Verify network connection\n"
                    "• Theme not applying: Check CSS syntax and required selectors\n"
                    "• Performance issues: Reduce timeline limit in settings\n"
                    "• Crashes: Check terminal for error messages\n\n"
                    "For more help, visit: https://github.com/your-repo/tootles",
                    classes="help-text"
                )

            # Action Buttons
            with Horizontal(classes="help-actions"):
                yield Button("Back", id="back-btn", variant="primary")
                yield Button("Settings", id="settings-btn", variant="default")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
        elif event.button.id == "settings-btn":
            from tootles.screens.settings import SettingsScreen
            self.app.push_screen(SettingsScreen(self.app_ref))

    DEFAULT_CSS = """
    HelpScreen {
        background: $surface;
        padding: 1;
    }

    .help-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 2;
        color: $primary;
        text-style: bold;
    }

    .help-section {
        margin-bottom: 2;
        padding: 1;
        border: solid $border;
        background: $surface;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $border;
        padding-bottom: 1;
    }

    .shortcut-row {
        height: 1;
        margin-bottom: 0;
    }

    .shortcut-key {
        width: 15;
        color: $accent;
        text-style: bold;
        content-align: left middle;
    }

    .shortcut-desc {
        width: 1fr;
        color: $text;
        content-align: left middle;
    }

    .help-text {
        color: $text;
        line-height: 1.4;
        margin: 1 0;
    }

    .help-actions {
        margin-top: 2;
        height: 3;
    }

    .help-actions Button {
        margin-right: 1;
    }
    """
