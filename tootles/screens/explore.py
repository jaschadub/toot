"""Explore screen for Tootles with trending content and search."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static

from tootles.screens.base import BaseScreen
from tootles.widgets.timeline import TimelineWidget

if TYPE_CHECKING:
    from tootles.main import TootlesApp


class ExploreScreen(BaseScreen):
    """Screen for exploring trending content and searching."""

    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "Explore"
        self.current_tab = "trending"

    def compose(self) -> ComposeResult:
        """Create the explore screen layout."""
        with Vertical():
            # Header with search
            with Horizontal(classes="explore-header"):
                yield Static("Explore", classes="screen-title")
                with Horizontal(classes="search-container"):
                    yield Input(placeholder="Search posts, users, hashtags...", id="search-input")
                    yield Button("Search", id="search-btn", variant="primary")

            # Tab Navigation
            with Horizontal(classes="explore-tabs"):
                yield Button("Trending", id="tab-trending", variant="primary", classes="explore-tab active")
                yield Button("Posts", id="tab-posts", variant="default", classes="explore-tab")
                yield Button("Hashtags", id="tab-hashtags", variant="default", classes="explore-tab")
                yield Button("Users", id="tab-users", variant="default", classes="explore-tab")
                yield Button("Local", id="tab-local", variant="default", classes="explore-tab")

            # Content Area
            with Vertical(id="explore-content"):
                # Trending Timeline (default)
                yield TimelineWidget(
                    self.app_ref,
                    timeline_type="trending",
                    id="trending-timeline"
                )

    async def on_mount(self) -> None:
        """Load trending content when screen is mounted."""
        await self.load_trending()

    async def load_trending(self) -> None:
        """Load trending posts."""
        try:
            timeline = self.query_one("#trending-timeline", TimelineWidget)
            await timeline.load_timeline()

        except Exception as e:
            self.app.notify(f"Failed to load trending content: {e}", severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-btn":
            await self.perform_search()
        elif event.button.id.startswith("tab-"):
            await self.handle_tab_change(event.button)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        if event.input.id == "search-input":
            await self.perform_search()

    async def handle_tab_change(self, button: Button) -> None:
        """Handle tab changes in explore screen."""
        # Update active tab
        for tab in self.query(".explore-tab"):
            tab.remove_class("active")
            tab.variant = "default"

        button.add_class("active")
        button.variant = "primary"

        # Extract tab type from button ID
        tab_type = button.id.replace("tab-", "")
        self.current_tab = tab_type

        # Load content for the selected tab
        await self.load_tab_content(tab_type)

    async def load_tab_content(self, tab_type: str) -> None:
        """Load content for the specified tab."""
        content_area = self.query_one("#explore-content", Vertical)

        # Clear existing content
        content_area.remove_children()

        if tab_type == "trending":
            timeline = TimelineWidget(
                self.app_ref,
                timeline_type="trending",
                id="trending-timeline"
            )
            content_area.mount(timeline)
            await timeline.load_timeline()

        elif tab_type == "posts":
            timeline = TimelineWidget(
                self.app_ref,
                timeline_type="public",
                id="posts-timeline"
            )
            content_area.mount(timeline)
            await timeline.load_timeline()

        elif tab_type == "local":
            timeline = TimelineWidget(
                self.app_ref,
                timeline_type="local",
                id="local-timeline"
            )
            content_area.mount(timeline)
            await timeline.load_timeline()

        elif tab_type == "hashtags":
            await self.load_trending_hashtags(content_area)

        elif tab_type == "users":
            await self.load_suggested_users(content_area)

    async def load_trending_hashtags(self, container: Vertical) -> None:
        """Load trending hashtags."""
        try:
            # Create hashtags display
            with container:
                yield Static("Trending Hashtags", classes="content-title")

                # Placeholder hashtags (would come from API)
                hashtags = [
                    ("#mastodon", "1.2k posts"),
                    ("#opensource", "856 posts"),
                    ("#python", "743 posts"),
                    ("#linux", "621 posts"),
                    ("#programming", "589 posts"),
                    ("#fediverse", "432 posts"),
                    ("#technology", "398 posts"),
                    ("#privacy", "287 posts"),
                ]

                for hashtag, count in hashtags:
                    with Horizontal(classes="hashtag-item"):
                        yield Button(hashtag, classes="hashtag-button")
                        yield Static(count, classes="hashtag-count")

        except Exception as e:
            self.app.notify(f"Failed to load hashtags: {e}", severity="error")

    async def load_suggested_users(self, container: Vertical) -> None:
        """Load suggested users to follow."""
        try:
            # Create users display
            container.mount(Static("Suggested Users", classes="content-title"))

            # Placeholder users (would come from API)
            users = [
                ("@alice@mastodon.social", "Alice Johnson", "Software Developer"),
                ("@bob@fosstodon.org", "Bob Smith", "Open Source Enthusiast"),
                ("@carol@mas.to", "Carol Davis", "Privacy Advocate"),
                ("@dave@hachyderm.io", "Dave Wilson", "Linux Admin"),
            ]

            for username, display_name, bio in users:
                with Horizontal(classes="user-item"):
                    with Vertical(classes="user-info"):
                        yield Static(display_name, classes="user-display-name")
                        yield Static(username, classes="user-username")
                        yield Static(bio, classes="user-bio")
                    yield Button("Follow", classes="follow-button")

        except Exception as e:
            self.app.notify(f"Failed to load suggested users: {e}", severity="error")

    async def perform_search(self) -> None:
        """Perform search based on input."""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()

        if not query:
            self.app.notify("Please enter a search term", severity="warning")
            return

        try:
            # Clear current content and show search results
            content_area = self.query_one("#explore-content", Vertical)
            content_area.remove_children()

            # Create search results timeline
            timeline = TimelineWidget(
                self.app_ref,
                timeline_type="search",
                search_query=query,
                id="search-timeline"
            )
            content_area.mount(timeline)
            await timeline.load_timeline()

            # Update tab state
            for tab in self.query(".explore-tab"):
                tab.remove_class("active")
                tab.variant = "default"

            self.app.notify(f"Searching for: {query}", severity="information")

        except Exception as e:
            self.app.notify(f"Search failed: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh current tab content."""
        self.run_worker(self.load_tab_content(self.current_tab))

    DEFAULT_CSS = """
    ExploreScreen {
        background: $surface;
    }

    .explore-header {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $border;
    }

    .screen-title {
        width: 15;
        text-style: bold;
        color: $primary;
        content-align: left middle;
    }

    .search-container {
        width: 1fr;
        height: 3;
    }

    #search-input {
        width: 1fr;
        margin-right: 1;
    }

    .explore-tabs {
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $border;
    }

    .explore-tab {
        margin-right: 1;
        min-width: 10;
    }

    .explore-tab.active {
        background: $primary;
        color: $text-primary;
    }

    #explore-content {
        height: 1fr;
        padding: 1;
    }

    .content-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        border-bottom: solid $border;
        padding-bottom: 1;
    }

    .hashtag-item {
        height: 3;
        margin-bottom: 1;
        padding: 0 1;
        border: solid $border;
        background: $surface;
    }

    .hashtag-button {
        width: 1fr;
        text-align: left;
        color: $accent;
    }

    .hashtag-count {
        width: 15;
        color: $text-muted;
        content-align: right middle;
    }

    .user-item {
        height: 5;
        margin-bottom: 1;
        padding: 1;
        border: solid $border;
        background: $surface;
    }

    .user-info {
        width: 1fr;
    }

    .user-display-name {
        text-style: bold;
        color: $text;
    }

    .user-username {
        color: $text-muted;
    }

    .user-bio {
        color: $text;
        margin-top: 1;
    }

    .follow-button {
        width: 10;
        height: 3;
    }
    """
