"""Account management screen for Tootles."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, Static, Switch

from tootles.screens.base import BaseScreen

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class AccountScreen(BaseScreen):
    """Account management screen for viewing and editing account settings."""

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Account Management"

    def compose(self) -> ComposeResult:
        """Create the account management screen layout."""
        with VerticalScroll():
            yield Static("Account Management", classes="account-title")

            # Account Information
            with Vertical(classes="account-section"):
                yield Label("Account Information", classes="section-title")

                with Horizontal(classes="field-row"):
                    yield Label("Username:", classes="field-label")
                    yield Static("@username@instance.social", id="username-display", classes="field-value")

                with Horizontal(classes="field-row"):
                    yield Label("Display Name:", classes="field-label")
                    yield Input(placeholder="Your display name", id="display-name", classes="field-input")

                with Horizontal(classes="field-row"):
                    yield Label("Bio:", classes="field-label")
                    yield Input(placeholder="Tell us about yourself", id="bio", classes="field-input")

                with Horizontal(classes="field-row"):
                    yield Label("Website:", classes="field-label")
                    yield Input(placeholder="https://your-website.com", id="website", classes="field-input")

            # Privacy Settings
            with Vertical(classes="account-section"):
                yield Label("Privacy Settings", classes="section-title")

                with Horizontal(classes="field-row"):
                    yield Label("Private Account:", classes="field-label")
                    yield Switch(id="private-account", classes="field-switch")

                with Horizontal(classes="field-row"):
                    yield Label("Require Follow Requests:", classes="field-label")
                    yield Switch(id="require-approval", classes="field-switch")

                with Horizontal(classes="field-row"):
                    yield Label("Hide Followers List:", classes="field-label")
                    yield Switch(id="hide-followers", classes="field-switch")

                with Horizontal(classes="field-row"):
                    yield Label("Hide Following List:", classes="field-label")
                    yield Switch(id="hide-following", classes="field-switch")

            # Content Settings
            with Vertical(classes="account-section"):
                yield Label("Content Settings", classes="section-title")

                with Horizontal(classes="field-row"):
                    yield Label("Default Post Visibility:", classes="field-label")
                    yield Static("Public", id="default-visibility", classes="field-value clickable")

                with Horizontal(classes="field-row"):
                    yield Label("Sensitive Content by Default:", classes="field-label")
                    yield Switch(id="sensitive-default", classes="field-switch")

                with Horizontal(classes="field-row"):
                    yield Label("Auto-delete Posts After:", classes="field-label")
                    yield Static("Never", id="auto-delete", classes="field-value clickable")

            # Statistics
            with Vertical(classes="account-section"):
                yield Label("Account Statistics", classes="section-title")

                with Horizontal(classes="stats-row"):
                    with Vertical(classes="stat-item"):
                        yield Static("0", classes="stat-number")
                        yield Static("Posts", classes="stat-label")

                    with Vertical(classes="stat-item"):
                        yield Static("0", classes="stat-number")
                        yield Static("Following", classes="stat-label")

                    with Vertical(classes="stat-item"):
                        yield Static("0", classes="stat-number")
                        yield Static("Followers", classes="stat-label")

            # Account Actions
            with Vertical(classes="account-section"):
                yield Label("Account Actions", classes="section-title")

                with Horizontal(classes="action-buttons"):
                    yield Button("Export Data", id="export-btn", variant="default")
                    yield Button("Import Data", id="import-btn", variant="default")
                    yield Button("Change Password", id="password-btn", variant="default")

                with Horizontal(classes="action-buttons"):
                    yield Button("Download Archive", id="archive-btn", variant="default")
                    yield Button("Request Verification", id="verify-btn", variant="default")
                    yield Button("Delete Account", id="delete-btn", variant="error")

            # Action Buttons
            with Horizontal(classes="form-actions"):
                yield Button("Save Changes", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Refresh", id="refresh-btn", variant="default")

    async def on_mount(self) -> None:
        """Load account information when screen is mounted."""
        await self.load_account_info()

    async def load_account_info(self) -> None:
        """Load current account information from the API."""
        try:
            if not self.app_ref.api_client:
                return

            # Get current user account info
            account = await self.app_ref.api_client.get_current_user()

            # Update display fields
            username_display = self.query_one("#username-display", Static)
            username_display.update(f"@{account.username}@{account.instance}")

            display_name_input = self.query_one("#display-name", Input)
            display_name_input.value = account.display_name or ""

            bio_input = self.query_one("#bio", Input)
            bio_input.value = account.note or ""

            website_input = self.query_one("#website", Input)
            website_input.value = account.url or ""

            # Update privacy switches
            private_switch = self.query_one("#private-account", Switch)
            private_switch.value = account.locked

            # Update statistics
            stats = self.query(".stat-number")
            if len(stats) >= 3:
                stats[0].update(str(account.statuses_count))
                stats[1].update(str(account.following_count))
                stats[2].update(str(account.followers_count))

        except Exception as e:
            self.app.notify(f"Failed to load account info: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "save-btn":
            await self.save_account_changes()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "refresh-btn":
            await self.load_account_info()
        elif event.button.id == "export-btn":
            self.app.notify("Export functionality not yet implemented", severity="warning")
        elif event.button.id == "import-btn":
            self.app.notify("Import functionality not yet implemented", severity="warning")
        elif event.button.id == "password-btn":
            self.app.notify("Password change must be done on your instance's website", severity="information")
        elif event.button.id == "archive-btn":
            self.app.notify("Archive download not yet implemented", severity="warning")
        elif event.button.id == "verify-btn":
            self.app.notify("Verification requests must be made on your instance's website", severity="information")
        elif event.button.id == "delete-btn":
            self.app.notify("Account deletion must be done on your instance's website", severity="warning")

    async def save_account_changes(self) -> None:
        """Save account changes to the server."""
        try:
            if not self.app_ref.api_client:
                self.app.notify("No API client available", severity="error")
                return

            # Get form values
            display_name = self.query_one("#display-name", Input).value
            bio = self.query_one("#bio", Input).value
            website = self.query_one("#website", Input).value
            private_account = self.query_one("#private-account", Switch).value

            # Update account via API
            await self.app_ref.api_client.update_account(
                display_name=display_name,
                note=bio,
                url=website,
                locked=private_account
            )

            self.app.notify("Account updated successfully", severity="success")

        except Exception as e:
            self.app.notify(f"Failed to update account: {e}", severity="error")

    DEFAULT_CSS = """
    AccountScreen {
        background: $surface;
        padding: 1;
    }

    .account-title {
        text-style: bold;
        text-align: center;
        margin-bottom: 2;
        color: $primary;
    }

    .account-section {
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

    .field-row {
        height: 3;
        margin-bottom: 1;
    }

    .field-label {
        width: 20;
        color: $text;
        content-align: left middle;
    }

    .field-value {
        width: 1fr;
        color: $text;
        content-align: left middle;
        padding-left: 1;
    }

    .field-value.clickable {
        color: $accent;
        text-style: underline;
    }

    .field-value.clickable:hover {
        color: $primary;
    }

    .field-input {
        width: 1fr;
    }

    .field-switch {
        width: auto;
        content-align: left middle;
    }

    .stats-row {
        height: 5;
    }

    .stat-item {
        width: 1fr;
        text-align: center;
    }

    .stat-number {
        text-style: bold;
        color: $primary;
        text-align: center;
    }

    .stat-label {
        color: $text-muted;
        text-align: center;
    }

    .action-buttons {
        height: 3;
        margin-bottom: 1;
    }

    .action-buttons Button {
        margin-right: 1;
    }

    .form-actions {
        margin-top: 2;
        height: 3;
    }

    .form-actions Button {
        margin-right: 1;
    }
    """
