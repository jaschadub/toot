# API Documentation

This document provides comprehensive API reference for tootles developers, theme creators, and contributors.

## Table of Contents

1. [Widget API](#widget-api)
2. [CSS Class Reference](#css-class-reference)
3. [Event System](#event-system)
4. [Extension Points](#extension-points)
5. [Theme API](#theme-api)
6. [Configuration API](#configuration-api)
7. [Mastodon API Client](#mastodon-api-client)

## Widget API

### Core Widgets

#### StatusWidget

Displays individual Mastodon statuses/toots.

```python
from tootles.widgets.status import StatusWidget
from tootles.api.models import Status

class StatusWidget(Widget):
    """Widget for displaying a single status/toot."""
    
    def __init__(self, status: Status, app_ref: "TootlesApp", **kwargs):
        """Initialize the status widget.
        
        Args:
            status: The Status object to display
            app_ref: Reference to the main application
        """
```

**Methods:**
- `handle_reply()` - Handle reply to status
- `handle_reblog()` - Handle reblog/boost of status  
- `handle_favorite()` - Handle favorite/unfavorite of status
- `handle_bookmark()` - Handle bookmark/unbookmark of status
- `update_action_buttons()` - Update button appearance based on status state

**Actions:**
- `action_toggle_favourite()` - Toggle favourite status
- `action_toggle_reblog()` - Toggle reblog status
- `action_reply()` - Reply to status
- `action_bookmark()` - Toggle bookmark status

#### TimelineWidget

Container for scrollable timeline of statuses.

```python
from tootles.widgets.timeline import TimelineWidget

class TimelineWidget(Widget):
    """Container widget for timeline with additional controls."""
    
    def __init__(
        self,
        statuses: Optional[List[Status]] = None,
        empty_message: str = "No statuses to display",
        load_callback: Optional[Callable] = None,
        **kwargs
    ):
```

**Methods:**
- `update_statuses(statuses, prepend=False)` - Update timeline with new statuses
- `append_statuses(statuses)` - Append statuses to timeline
- `get_statuses()` - Get current list of statuses
- `clear()` - Clear all statuses
- `set_loading(loading)` - Set loading state

**Messages:**
- `StatusSelected(status)` - Emitted when status is selected
- `LoadMore(direction)` - Emitted when more statuses should be loaded

#### ComposeWidget

Modal screen for composing new toots.

```python
from tootles.widgets.compose import ComposeWidget

class ComposeWidget(ModalScreen):
    """Modal screen for composing new toots."""
    
    def __init__(
        self,
        app_ref: "TootlesApp",
        reply_to: Optional["Status"] = None,
        initial_content: str = "",
        **kwargs
    ):
```

**Methods:**
- `_update_char_counter()` - Update character counter display
- `_post_status()` - Post the composed status

**Actions:**
- `action_cancel()` - Cancel compose (Escape key)

### Base Classes

#### BaseScreen

Base class for all tootles screens.

```python
from tootles.screens.base import BaseScreen

class BaseScreen(Screen):
    """Base class for all Tootles screens."""
    
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Search"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("escape", "back", "Back"),
    ]
    
    def __init__(self, app_ref: "TootlesApp"):
```

**Methods:**
- `action_command_palette()` - Open fuzzy search command palette
- `action_refresh()` - Refresh current screen content
- `action_back()` - Go back to previous screen
- `is_configured()` - Check if app is properly configured
- `show_configuration_needed()` - Show configuration message

## CSS Class Reference

### Layout Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.app-container` | Main application container | Root element styling |
| `.screen-container` | Individual screen container | Screen-level styling |
| `.sidebar-navigation` | Navigation sidebar | Navigation panel |
| `.main-content` | Main content area | Primary content region |

### Navigation Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.nav-item` | Navigation item | Individual nav buttons |
| `.nav-item--active` | Active navigation item | Currently selected nav |
| `.nav-item--home` | Home navigation item | Home-specific styling |
| `.nav-item--notifications` | Notifications nav item | Notifications styling |

### Status Display Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.status-list` | Status list container | Timeline container |
| `.status-item` | Individual status | Single toot styling |
| `.status-item--focused` | Focused status | Selected status |
| `.status-header` | Status header info | Author/timestamp area |
| `.status-content` | Status text content | Main toot content |
| `.status-actions` | Status action buttons | Interaction buttons |
| `.status-metadata` | Status metadata | Additional info |

### Interactive Element Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.button` | Generic button | All buttons |
| `.button--primary` | Primary button | Main action buttons |
| `.button--secondary` | Secondary button | Alternative actions |
| `.button--danger` | Danger button | Destructive actions |
| `.input-field` | Input field | Text inputs |
| `.search-box` | Search input | Search interfaces |

### Widget-Specific Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.timeline-widget` | Timeline container | Timeline styling |
| `.timeline-header` | Timeline header | Timeline title area |
| `.timeline-content` | Timeline content | Scrollable content |
| `.timeline-loading` | Loading indicator | Loading state |
| `.timeline-error` | Error message | Error state |
| `.timeline-empty` | Empty message | No content state |

### Compose Widget Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.compose-widget` | Compose container | Compose modal |
| `.compose-header` | Compose header | Title area |
| `.compose-textarea` | Text input area | Main text input |
| `.compose-controls` | Control buttons | Action buttons |
| `.compose-char-count` | Character counter | Count display |
| `.compose-char-count--warning` | Warning state | Near limit |
| `.compose-char-count--error` | Error state | Over limit |

### State Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.loading` | Loading state | Loading indicators |
| `.error-message` | Error message | Error displays |
| `.warning-message` | Warning message | Warning displays |
| `.info-message` | Info message | Information displays |
| `.success-message` | Success message | Success displays |

### Utility Classes

| Class | Purpose | Usage |
|-------|---------|-------|
| `.scrollable` | Scrollable container | Scroll styling |
| `.focusable` | Focusable element | Focus indicators |
| `.hidden` | Hidden element | Hide elements |

## Event System

### Widget Messages

#### Timeline Events

```python
# Status selection
class StatusSelected(Message):
    def __init__(self, status: Status) -> None:
        self.status = status

# Load more content
class LoadMore(Message):
    def __init__(self, direction: str = "older") -> None:
        self.direction = direction  # "older" or "newer"
```

#### Compose Events

```python
# Post status
class PostStatus(Message):
    def __init__(self, content: str, visibility: str, **kwargs) -> None:
        self.content = content
        self.visibility = visibility
        # Additional fields: in_reply_to_id, sensitive, spoiler_text

# Cancel compose
class Cancel(Message):
    pass
```

### Event Handling

```python
# Handle status selection
async def on_timeline_status_selected(self, event: Timeline.StatusSelected) -> None:
    """Handle status selection events."""
    status = event.status
    # Process selected status

# Handle load more
async def on_timeline_load_more(self, event: Timeline.LoadMore) -> None:
    """Handle load more requests."""
    direction = event.direction
    # Load more content
```

### Custom Events

Create custom events by extending `Message`:

```python
from textual.message import Message

class CustomEvent(Message):
    def __init__(self, data: Any) -> None:
        self.data = data
        super().__init__()

# Emit event
await self.post_message(CustomEvent(my_data))

# Handle event
async def on_custom_event(self, event: CustomEvent) -> None:
    data = event.data
    # Process event
```

## Extension Points

### Custom Screens

Create custom screens by extending `BaseScreen`:

```python
from tootles.screens.base import BaseScreen

class MyCustomScreen(BaseScreen):
    """Custom screen implementation."""
    
    def __init__(self, app_ref: "TootlesApp"):
        super().__init__(app_ref)
        self.title = "My Custom Screen"
    
    def compose(self) -> ComposeResult:
        """Create the screen layout."""
        yield Label("Custom content here")
    
    async def action_refresh(self) -> None:
        """Custom refresh implementation."""
        self.notify("Refreshing custom screen...")
```

### Custom Widgets

Create custom widgets by extending Textual widgets:

```python
from textual.widget import Widget
from textual.app import ComposeResult

class MyCustomWidget(Widget):
    """Custom widget implementation."""
    
    DEFAULT_CSS = """
    MyCustomWidget {
        height: auto;
        background: $surface;
        border: solid $border;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Label("Custom widget content")
    
    def on_mount(self) -> None:
        """Handle widget mounting."""
        self.can_focus = True
```

### Plugin System

Extend tootles functionality with plugins:

```python
class TootlesPlugin:
    """Base plugin interface."""
    
    def __init__(self, app: "TootlesApp"):
        self.app = app
    
    def initialize(self) -> None:
        """Initialize plugin."""
        pass
    
    def register_screens(self) -> Dict[str, Type[Screen]]:
        """Register custom screens."""
        return {}
    
    def register_commands(self) -> List[Command]:
        """Register command palette commands."""
        return []
```

## Theme API

### ThemeManager

Manages theme loading, validation, and hot-reload.

```python
from tootles.themes.manager import ThemeManager

class ThemeManager:
    """Enhanced theme manager with CSS loading and validation."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_theme: Optional[str] = None
        self.current_css: Optional[str] = None
```

**Methods:**
- `get_available_themes()` - Get list of available theme names
- `get_theme_path(theme_name)` - Get path to theme file
- `get_theme_info(theme_name)` - Get theme metadata
- `load_theme(theme_name)` - Load and apply theme
- `validate_theme_content(css_content)` - Validate CSS content
- `reload_current_theme()` - Reload current theme
- `export_theme_template(output_path)` - Export community template

### Theme Validation

```python
# Validate theme
validation_result = theme_manager.validate_theme_content(css_content)
is_valid, message = validation_result

if not is_valid:
    print(f"Theme validation failed: {message}")
```

### Required Selectors

Themes must include these selectors:

```python
REQUIRED_SELECTORS = {
    ".app-container",
    ".status-item", 
    ".timeline-widget",
    ".compose-widget",
    ".button",
    ".input-field"
}
```

## Configuration API

### ConfigManager

Manages configuration loading, saving, and validation.

```python
from tootles.config.manager import ConfigManager

class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
```

**Methods:**
- `save()` - Save current configuration
- `reload()` - Reload configuration from file
- `get_config_dir()` - Get configuration directory
- `is_configured()` - Check if properly configured

### Configuration Schema

```python
from tootles.config.schema import TootlesConfig

@dataclass
class TootlesConfig:
    """Main configuration structure."""
    
    # Instance settings
    instance_url: str = ""
    access_token: str = ""
    
    # UI settings
    theme: str = "default"
    auto_refresh: bool = True
    refresh_interval: int = 60
    
    # Theme settings
    theme_directory: str = "~/.config/tootles/themes"
    enable_theme_hot_reload: bool = False
```

**Methods:**
- `get_theme_directory()` - Get theme directory as Path
- `validate()` - Validate configuration values

## Mastodon API Client

### MastodonClient

Async client for Mastodon API interactions.

```python
from tootles.api.client import MastodonClient

class MastodonClient:
    """Async Mastodon API client."""
    
    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url
        self.access_token = access_token
```

**Timeline Methods:**
- `get_home_timeline(**params)` - Get home timeline
- `get_local_timeline(**params)` - Get local timeline  
- `get_federated_timeline(**params)` - Get federated timeline
- `get_notifications(**params)` - Get notifications

**Status Methods:**
- `post_status(content, **params)` - Post new status
- `get_status(status_id)` - Get status by ID
- `delete_status(status_id)` - Delete status
- `reblog_status(status_id)` - Reblog status
- `unreblog_status(status_id)` - Unreblog status
- `favorite_status(status_id)` - Favorite status
- `unfavorite_status(status_id)` - Unfavorite status
- `bookmark_status(status_id)` - Bookmark status
- `unbookmark_status(status_id)` - Unbookmark status

**Search Methods:**
- `search(query, **params)` - Search content
- `search_accounts(query, **params)` - Search accounts
- `search_hashtags(query, **params)` - Search hashtags

### Data Models

#### Status Model

```python
from tootles.api.models import Status

@dataclass
class Status:
    """Represents a Mastodon status (toot)."""
    
    id: str
    uri: str
    created_at: datetime
    account: Account
    content: str
    visibility: str
    sensitive: bool
    spoiler_text: str
    media_attachments: List[MediaAttachment]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    favourited: bool
    reblogged: bool
    bookmarked: bool
    # ... additional fields
```

#### Account Model

```python
from tootles.api.models import Account

@dataclass  
class Account:
    """Represents a Mastodon account."""
    
    id: str
    username: str
    acct: str
    display_name: str
    locked: bool
    bot: bool
    created_at: datetime
    note: str
    url: str
    avatar: str
    followers_count: int
    following_count: int
    statuses_count: int
    # ... additional fields
```

### Error Handling

```python
from tootles.api.client import MastodonAPIError

try:
    status = await client.post_status("Hello, Mastodon!")
except MastodonAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
```

## Development Guidelines

### Widget Development

1. **Extend base classes** when possible
2. **Define DEFAULT_CSS** for styling
3. **Implement proper focus handling**
4. **Use semantic class names**
5. **Handle errors gracefully**

### Event Handling

1. **Use specific event types**
2. **Stop event propagation** when appropriate
3. **Handle async operations** properly
4. **Provide error feedback**

### Theme Development

1. **Include all required selectors**
2. **Use CSS variables** for consistency
3. **Test accessibility** (contrast, focus)
4. **Document color choices**
5. **Validate CSS syntax**

### API Integration

1. **Handle rate limiting**
2. **Implement proper caching**
3. **Use async/await** consistently
4. **Provide error recovery**
5. **Log API interactions**

## Examples

See the `examples/` directory for:
- Custom widget implementations
- Theme development examples
- Plugin development templates
- API usage patterns

## Contributing

When contributing to the API:

1. **Maintain backward compatibility**
2. **Document all public methods**
3. **Include type hints**
4. **Add comprehensive tests**
5. **Update this documentation**

For detailed contribution guidelines, see [`CONTRIBUTING.md`](CONTRIBUTING.md).