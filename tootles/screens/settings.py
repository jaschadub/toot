"""Settings screen for Tootles configuration."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from tootles.screens.base import BaseScreen

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class SettingsScreen(BaseScreen):
    """Settings screen for configuring Tootles."""

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Settings"

    def compose(self) -> ComposeResult:
        """Create the settings screen layout."""
        with VerticalScroll():
            yield Static("Tootles Settings", classes="settings-title")

            # Instance Settings
            with Vertical(classes="settings-section"):
                yield Label("Instance Settings", classes="section-title")

                with Horizontal(classes="setting-row"):
                    yield Label("Instance URL:", classes="setting-label")
                    yield Input(
                        value=self.config_manager.config.instance_url,
                        placeholder="https://mastodon.social",
                        id="instance-url",
                        classes="setting-input"
                    )

                with Horizontal(classes="setting-row"):
                    yield Label("Access Token:", classes="setting-label")
                    yield Input(
                        value=self.config_manager.config.access_token,
                        password=True,
                        placeholder="Your access token",
                        id="access-token",
                        classes="setting-input"
                    )

            # Theme Settings
            with Vertical(classes="settings-section"):
                yield Label("Theme Settings", classes="section-title")

                with Horizontal(classes="setting-row"):
                    yield Label("Theme:", classes="setting-label")
                    theme_options = [(theme, theme.title()) for theme in self.theme_manager.get_available_themes()]
                    # Create Select without initial value to avoid validation error during creation
                    yield Select(
                        options=theme_options,
                        id="theme-select",
                        classes="setting-select"
                    )

                with Horizontal(classes="setting-row"):
                    yield Label("Enable Hot Reload:", classes="setting-label")
                    yield Checkbox(
                        value=self.config_manager.config.enable_theme_hot_reload,
                        id="hot-reload-checkbox",
                        classes="setting-checkbox"
                    )

            # UI Settings
            with Vertical(classes="settings-section"):
                yield Label("UI Settings", classes="section-title")

                with Horizontal(classes="setting-row"):
                    yield Label("Auto Refresh:", classes="setting-label")
                    yield Checkbox(
                        value=self.config_manager.config.auto_refresh,
                        id="auto-refresh-checkbox",
                        classes="setting-checkbox"
                    )

                with Horizontal(classes="setting-row"):
                    yield Label("Refresh Interval (seconds):", classes="setting-label")
                    yield Input(
                        value=str(self.config_manager.config.refresh_interval),
                        id="refresh-interval",
                        classes="setting-input"
                    )

                with Horizontal(classes="setting-row"):
                    yield Label("Show Media Previews:", classes="setting-label")
                    yield Checkbox(
                        value=self.config_manager.config.show_media_previews,
                        id="media-previews-checkbox",
                        classes="setting-checkbox"
                    )

            # Timeline Settings
            with Vertical(classes="settings-section"):
                yield Label("Timeline Settings", classes="section-title")

                with Horizontal(classes="setting-row"):
                    yield Label("Timeline Limit:", classes="setting-label")
                    yield Input(
                        value=str(self.config_manager.config.timeline_limit),
                        id="timeline-limit",
                        classes="setting-input"
                    )

                with Horizontal(classes="setting-row"):
                    yield Label("Enable Streaming:", classes="setting-label")
                    yield Checkbox(
                        value=self.config_manager.config.enable_streaming,
                        id="streaming-checkbox",
                        classes="setting-checkbox"
                    )

            # Action Buttons
            with Horizontal(classes="settings-actions"):
                yield Button("Save Settings", id="save-btn", variant="primary")
                yield Button("Reset to Defaults", id="reset-btn", variant="default")
                yield Button("Export Theme Template", id="export-template-btn", variant="default")
                yield Button("Back", id="back-btn", variant="default")

    async def on_mount(self) -> None:
        """Set initial values after mount."""
        # Set the initial theme value after the Select widget is fully initialized
        try:
            theme_select = self.query_one("#theme-select", Select)
            current_theme = self.config_manager.config.theme
            available_themes = self.theme_manager.get_available_themes()
            if current_theme in available_themes:
                theme_select.value = current_theme
            elif available_themes:
                theme_select.value = available_themes[0]
        except Exception as e:
            # If setting the value fails, just log it and continue
            self.notify(f"Could not set initial theme: {e}", severity="warning")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "save-btn":
            await self._save_settings()
        elif event.button.id == "reset-btn":
            await self._reset_settings()
        elif event.button.id == "export-template-btn":
            await self._export_theme_template()
        elif event.button.id == "back-btn":
            self.app.pop_screen()

    async def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select widget changes."""
        if event.select.id == "theme-select":
            # Apply theme immediately for preview
            try:
                await self.theme_manager.load_theme(event.value)
                self.notify(f"Theme changed to {event.value}")
            except Exception as e:
                self.notify(f"Error loading theme: {e}", severity="error")

    async def _save_settings(self) -> None:
        """Save current settings."""
        try:
            # Get values from inputs
            instance_url = self.query_one("#instance-url", Input).value
            access_token = self.query_one("#access-token", Input).value
            theme = self.query_one("#theme-select", Select).value
            hot_reload = self.query_one("#hot-reload-checkbox", Checkbox).value
            auto_refresh = self.query_one("#auto-refresh-checkbox", Checkbox).value
            refresh_interval = int(self.query_one("#refresh-interval", Input).value)
            media_previews = self.query_one("#media-previews-checkbox", Checkbox).value
            timeline_limit = int(self.query_one("#timeline-limit", Input).value)
            streaming = self.query_one("#streaming-checkbox", Checkbox).value

            # Update config
            self.config_manager.config.instance_url = instance_url
            self.config_manager.config.access_token = access_token
            self.config_manager.config.theme = theme
            self.config_manager.config.enable_theme_hot_reload = hot_reload
            self.config_manager.config.auto_refresh = auto_refresh
            self.config_manager.config.refresh_interval = refresh_interval
            self.config_manager.config.show_media_previews = media_previews
            self.config_manager.config.timeline_limit = timeline_limit
            self.config_manager.config.enable_streaming = streaming

            # Validate and save
            self.config_manager.config.validate()
            self.config_manager.save()

            self.notify("Settings saved successfully!", severity="information")

        except ValueError as e:
            self.notify(f"Invalid input: {e}", severity="error")
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error")

    async def _reset_settings(self) -> None:
        """Reset settings to defaults."""
        try:
            # Create default config
            from tootles.config.schema import TootlesConfig
            default_config = TootlesConfig()

            # Update inputs with default values
            self.query_one("#instance-url", Input).value = default_config.instance_url
            self.query_one("#access-token", Input).value = default_config.access_token

            # Handle theme select more carefully
            theme_select = self.query_one("#theme-select", Select)
            available_themes = self.theme_manager.get_available_themes()
            if default_config.theme in available_themes:
                theme_select.value = default_config.theme
            elif available_themes:
                # Fall back to first available theme if default not available
                theme_select.value = available_themes[0]

            self.query_one("#hot-reload-checkbox", Checkbox).value = (
                default_config.enable_theme_hot_reload
            )
            self.query_one("#auto-refresh-checkbox", Checkbox).value = (
                default_config.auto_refresh
            )
            self.query_one("#refresh-interval", Input).value = str(
                default_config.refresh_interval
            )
            self.query_one("#media-previews-checkbox", Checkbox).value = (
                default_config.show_media_previews
            )
            self.query_one("#timeline-limit", Input).value = str(
                default_config.timeline_limit
            )
            self.query_one("#streaming-checkbox", Checkbox).value = (
                default_config.enable_streaming
            )

            self.notify("Settings reset to defaults", severity="information")

        except Exception as e:
            self.notify(f"Error resetting settings: {e}", severity="error")

    async def _export_theme_template(self) -> None:
        """Export theme template to user directory."""
        try:
            theme_dir = self.theme_manager.create_user_theme_directory()
            template_path = theme_dir / "my-custom-theme.css"

            self.theme_manager.export_theme_template(template_path)
            self.notify(
                f"Theme template exported to {template_path}",
                severity="information"
            )

        except Exception as e:
            self.notify(f"Error exporting template: {e}", severity="error")

    DEFAULT_CSS = """
    SettingsScreen {
        background: $surface;
        padding: 1;
    }

    .settings-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 2;
        color: $primary;
    }

    .settings-section {
        margin-bottom: 2;
        padding: 1;
        border: solid $border;
        background: $surface;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .setting-row {
        height: 3;
        margin-bottom: 1;
    }

    .setting-label {
        width: 25;
        content-align: left middle;
        color: $text;
    }

    .setting-input {
        width: 1fr;
        margin-left: 1;
    }

    .setting-select {
        width: 1fr;
        margin-left: 1;
    }

    .setting-checkbox {
        margin-left: 1;
    }

    .settings-actions {
        margin-top: 2;
        height: 3;
    }

    .settings-actions Button {
        margin-right: 1;
    }
    """
