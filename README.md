# Tootles

A modern Textual-based Mastodon client with web UI parity and advanced theming.

## Features

- **Web UI Alignment**: All major Mastodon web sections (Home, Notifications, Explore, etc.)
- **Modern CSS Theming**: Community-driven theme repository with hot-reload
- **Fuzzy Search**: Command palette for quick navigation and Mastodon search
- **Real-time Updates**: Live feeds with streaming timeline updates
- **Enhanced UX**: Textual-native interactions and animations

## Installation

### From Source

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

## Configuration

On first run, Tootles will create a configuration file at `~/.config/tootles/config.toml`.

You need to configure your Mastodon instance:

```toml
# Instance settings
instance_url = "https://mastodon.social"
access_token = "your_access_token_here"

# UI settings
theme = "default"
auto_refresh = true
refresh_interval = 60
```

### Getting an Access Token

1. Go to your Mastodon instance's settings
2. Navigate to Development → New Application
3. Create a new application with appropriate scopes
4. Copy the access token to your configuration

## Usage

```bash
# Run Tootles
tootles

# Run with custom config
tootles --config /path/to/config.toml
```

### Keyboard Shortcuts

- `Ctrl+Q`: Quit
- `Ctrl+P`: Open command palette
- `Ctrl+R`: Refresh current screen
- `Ctrl+T`: Toggle theme
- `H`: Home timeline
- `N`: Notifications
- `E`: Explore
- `B`: Bookmarks
- `F`: Favorites
- `L`: Lists
- `C`: Compose
- `S`: Settings

## Themes

Tootles supports custom CSS themes. Built-in themes include:

- `default`: Default theme
- `dark`: Dark theme
- `light`: Light theme

### Custom Themes

Place custom theme files in `~/.config/tootles/themes/`:

```css
/* ~/.config/tootles/themes/my-theme.css */
.app-container {
    background: #1a1a1a;
    color: #ffffff;
}

.status-item {
    background: #2a2a2a;
    border: solid #444444;
}
```

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
└── themes-community/        # Community themes
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Theme Contributions

Community themes are welcome! See the `themes-community/` directory for examples and contribution guidelines.

## License

GPL-3.0 License - see LICENSE file for details.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/)
- Inspired by the original [toot](https://github.com/ihabunek/toot) client
- Mastodon API integration