# Tootles

A modern Textual-based Mastodon client with web UI parity and advanced theming.

## Features

- **🌐 Web UI Parity**: All major Mastodon web sections (Home, Notifications, Explore, etc.)
- **🎨 Advanced Theming**: CSS-based theming system with community themes and hot-reload
- **🔍 Fuzzy Search**: Command palette for quick navigation and Mastodon search
- **📡 Real-time Updates**: Live feeds with streaming timeline updates
- **✨ Enhanced UX**: Textual-native interactions and animations
- **⌨️ Keyboard First**: Full keyboard navigation with mouse support
- **🔖 Complete Features**: Bookmarks, favorites, lists, compose, and more

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
git clone https://github.com/tootles-dev/tootles.git
cd tootles
pip install -e .
```

### Development Setup

```bash
git clone https://github.com/tootles-dev/tootles.git
cd tootles
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Quick Start

### 1. First Run

```bash
tootles
```

This creates a configuration file at `~/.config/tootles/config.toml`.

### 2. Configure Your Instance

Edit the configuration file:

```toml
# Instance settings
instance_url = "https://your-mastodon-instance.social"
access_token = "your_access_token_here"

# UI settings
theme = "default"
auto_refresh = true
refresh_interval = 60
```

### 3. Get an Access Token

1. Go to your Mastodon instance's settings
2. Navigate to **Development** → **New Application**
3. Create a new application with these scopes:
   - `read` - Read access to your account
   - `write` - Post statuses and interact
   - `follow` - Follow/unfollow accounts
4. Copy the **Access Token** to your configuration

### 4. Launch Tootles

```bash
tootles
```

You should now see your home timeline!

## Usage

### Navigation

Use these keyboard shortcuts to navigate:

| Key | Action |
|-----|--------|
| `H` | Home timeline |
| `N` | Notifications |
| `E` | Explore |
| `L` | Local timeline |
| `F` | Federated timeline |
| `B` | Bookmarks |
| `⭐` | Favorites |
| `📋` | Lists |
| `C` | Compose new toot |
| `S` | Settings |

### Global Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+Q` | Quit application |
| `Ctrl+P` | Open command palette |
| `Ctrl+R` | Refresh current screen |
| `Ctrl+T` | Toggle theme |
| `Escape` | Go back/cancel |

### Status Interactions

| Key | Action |
|-----|--------|
| `Enter` | View status details |
| `R` | Reply to status |
| `B` | Boost/reblog status |
| `F` | Favorite status |
| `K` | Bookmark status |
| `↑/↓` | Navigate statuses |

### Command Palette

Press `Ctrl+P` to open the fuzzy search command palette:

- **Navigation**: Type screen names (home, notifications, explore)
- **Search**: Search for users, hashtags, or posts
- **Actions**: Quick actions like refresh, toggle theme
- **Recent**: Access recently used commands

## Configuration

### Configuration File

Location: `~/.config/tootles/config.toml`

```toml
# Instance settings
instance_url = "https://mastodon.social"
access_token = "your_access_token"

# UI settings
theme = "default"
auto_refresh = true
refresh_interval = 60
show_media_previews = true

# Timeline settings
timeline_limit = 40
enable_streaming = true
mark_notifications_read = true

# Search settings
search_history_size = 100
enable_fuzzy_search = true

# Theme settings
theme_directory = "~/.config/tootles/themes"
enable_theme_hot_reload = false

# Advanced settings
cache_size = 1000
rate_limit_requests = 300
rate_limit_window = 300
```

### Custom Configuration

Run with a custom configuration file:

```bash
tootles --config /path/to/custom-config.toml
```

## Themes

### Built-in Themes

- `default` - Default theme with balanced colors
- `dark` - Dark theme for low-light environments
- `light` - Light theme for bright environments
- `high-contrast` - High contrast theme for accessibility

### Changing Themes

1. **Via Configuration**:
   ```toml
   theme = "dark"
   ```

2. **Via Settings Screen**: Press `S` and navigate to theme settings

3. **Via Command Palette**: Press `Ctrl+P` and type "theme"

### Custom Themes

Create custom themes in `~/.config/tootles/themes/`:

```bash
# Export the community template
tootles --export-template ~/.config/tootles/themes/my-theme.css
```

Edit the template and customize colors:

```css
/* My Custom Theme */
.app-container {
    background: #1a1a1a;
    color: #ffffff;
}

.status-item {
    background: #2a2a2a;
    border: solid #444444;
}

.button {
    background: #0066cc;
    color: #ffffff;
}
```

See [`THEME_DEVELOPMENT.md`](THEME_DEVELOPMENT.md) for detailed theming guide.

### Hot Reload (Development)

Enable hot reload for theme development:

```toml
enable_theme_hot_reload = true
```

Changes to theme files will automatically reload.

## Screens

### Home Timeline

- View posts from accounts you follow
- Real-time updates with streaming
- Infinite scroll pagination
- Interactive status actions (reply, boost, favorite, bookmark)

### Notifications

- Filtered by type: mentions, favorites, boosts, follows, polls
- Grouped notifications
- Mark as read functionality
- Quick action buttons

### Explore

- Trending posts and hashtags
- User discovery suggestions
- Search functionality
- Content filtering options

### Local & Federated Timelines

- Local: Posts from your instance
- Federated: Posts from connected instances
- Real-time streaming updates
- Same interaction features as home timeline

### Compose

- Rich text composition
- Character counter with warnings
- Visibility settings (public, unlisted, followers-only, direct)
- Reply threading
- Content warnings and sensitive media

### Bookmarks & Favorites

- View your bookmarked posts
- Browse favorited content
- Same interaction features
- Search and filter options

### Lists

- View and manage your lists
- Browse list timelines
- Add/remove accounts from lists

## Advanced Features

### Streaming Updates

Real-time timeline updates using Mastodon's streaming API:

```toml
enable_streaming = true
```

### Search

- **Global Search**: Find users, hashtags, and posts across Mastodon
- **Fuzzy Search**: Command palette with intelligent matching
- **Search History**: Recent searches saved automatically

### Media Support

- Image previews in timeline
- Media viewer for full-size images
- Video and audio file indicators
- Configurable media preview settings

### Accessibility

- Full keyboard navigation
- High contrast themes
- Screen reader friendly
- Configurable font sizes
- Color blind friendly options

## Troubleshooting

### Common Issues

#### Authentication Errors

**Problem**: "Invalid credentials" or "Unauthorized"

**Solution**:
1. Verify `instance_url` includes `https://`
2. Check `access_token` is correct and has proper scopes
3. Generate a new token if needed

#### Theme Not Loading

**Problem**: Custom theme doesn't appear

**Solution**:
1. Check theme file exists in `~/.config/tootles/themes/`
2. Verify filename matches config setting (without `.css`)
3. Validate CSS syntax

#### Performance Issues

**Problem**: Slow loading or high memory usage

**Solution**:
1. Reduce `timeline_limit` setting
2. Disable streaming: `enable_streaming = false`
3. Reduce `cache_size`
4. Close other terminal applications

#### Configuration Not Found

**Problem**: Settings not persisting

**Solution**:
1. Check config directory exists: `~/.config/tootles/`
2. Verify file permissions
3. Run with explicit config: `tootles --config /path/to/config.toml`

### Debug Mode

Enable debug logging:

```toml
debug_mode = true
```

Logs are saved to `~/.config/tootles/logs/`

### Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/tootles-dev/tootles/issues)
- **Discussions**: [Community forum](https://github.com/tootles-dev/tootles/discussions)
- **Documentation**: See additional guides in the repository

## Migration from toot

Migrating from the original toot client? See [`MIGRATION.md`](MIGRATION.md) for a complete migration guide.

## Development

### Project Structure

```
tootles/
├── tootles/
│   ├── main.py              # Main application
│   ├── config/              # Configuration management
│   ├── screens/             # UI screens
│   ├── widgets/             # UI widgets
│   ├── themes/              # Theme management
│   ├── api/                 # Mastodon API client
│   └── cli/                 # CLI interface
├── tests/                   # Test suite
└── docs/                    # Documentation
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .

# Run security checks
bandit -r tootles/
```

### Code Quality

This project uses:

- **ruff**: Fast Python linter
- **black**: Code formatter
- **bandit**: Security linter
- **mypy**: Type checking
- **pytest**: Testing framework

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and linting: `pytest && ruff check .`
5. Submit a pull request

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed contribution guidelines.

### Theme Contributions

Community themes are welcome! See [`THEME_DEVELOPMENT.md`](THEME_DEVELOPMENT.md) for the complete theming guide.

## Architecture

Tootles is built with:

- **[Textual](https://textual.textualize.io/)**: Modern TUI framework
- **[aiohttp](https://docs.aiohttp.org/)**: Async HTTP client
- **[httpx](https://www.python-httpx.org/)**: HTTP client with streaming support
- **Python 3.8+**: Modern Python features

See [`TOOTLES_ARCHITECTURE.md`](TOOTLES_ARCHITECTURE.md) for detailed architecture documentation.

## License

GPL-3.0 License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) by Textualize
- Inspired by the original [toot](https://github.com/ihabunek/toot) client by Ivan Habunek
- Mastodon API integration
- Community theme contributors

---

**Happy tooting!** 🐘✨