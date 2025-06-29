# Migration Guide: From toot to tootles

This guide helps you migrate from the original [toot](https://github.com/ihabunek/toot) Mastodon CLI client to tootles, the modern Textual-based client with enhanced theming and web UI parity.

## Overview

Tootles is a hard fork of toot that migrates from urwid to the Textual framework, providing:

- **Modern UI**: Web UI parity with all major Mastodon sections
- **Advanced Theming**: CSS-based theming system with community themes
- **Enhanced UX**: Textual-native interactions and animations
- **Real-time Updates**: Live feeds with streaming timeline updates
- **Command Palette**: Fuzzy search for quick navigation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install tootles

```bash
# From source (recommended for latest features)
git clone https://github.com/tootles-dev/tootles.git
cd tootles
pip install -e .

# Or install from PyPI (when available)
pip install tootles
```

## Configuration Migration

### Step 1: Locate Your toot Configuration

The original toot stores configuration in:
- **Linux/macOS**: `~/.config/toot/`
- **Windows**: `%APPDATA%\toot\`

Key files:
- `config.json`: Instance and account information
- `user.json`: User preferences

### Step 2: Extract toot Settings

From your toot configuration, you'll need:

```json
// ~/.config/toot/config.json
{
  "apps": {
    "your-instance.social": {
      "base_url": "https://your-instance.social",
      "client_id": "...",
      "client_secret": "..."
    }
  },
  "users": {
    "username@your-instance.social": {
      "instance": "your-instance.social",
      "username": "username",
      "access_token": "your-access-token"
    }
  }
}
```

### Step 3: Configure tootles

Run tootles for the first time to create the configuration:

```bash
tootles
```

This creates `~/.config/tootles/config.toml`. Edit it with your settings:

```toml
# Instance settings
instance_url = "https://your-instance.social"
access_token = "your-access-token"

# UI settings
theme = "default"
auto_refresh = true
refresh_interval = 60
show_media_previews = true

# Timeline settings
timeline_limit = 40
enable_streaming = true
mark_notifications_read = true
```

### Step 4: Verify Configuration

Test your configuration:

```bash
tootles
```

You should see your home timeline. If you get authentication errors, verify your `instance_url` and `access_token`.

## Feature Comparison

| Feature | toot | tootles | Notes |
|---------|------|---------|-------|
| **Core Functionality** |
| Home timeline | ✅ | ✅ | Enhanced with real-time updates |
| Post status | ✅ | ✅ | Improved compose interface |
| Reply/boost/favorite | ✅ | ✅ | Interactive buttons |
| Notifications | ✅ | ✅ | Filtered by type |
| Search | ✅ | ✅ | Enhanced with fuzzy search |
| **UI/UX** |
| Terminal interface | urwid | Textual | Modern framework |
| Theming | Limited | CSS-based | Community themes |
| Navigation | Key-based | Key + mouse | Enhanced interaction |
| Real-time updates | ❌ | ✅ | Streaming support |
| **Advanced Features** |
| Command palette | ❌ | ✅ | Fuzzy search navigation |
| Hot-reload themes | ❌ | ✅ | Development feature |
| Web UI parity | Partial | Full | All major sections |
| Media previews | Basic | Enhanced | Better handling |

## Command Migration

### toot Commands → tootles Equivalents

| toot Command | tootles Equivalent | Notes |
|--------------|-------------------|-------|
| `toot tui` | `tootles` | Main interface |
| `toot post "text"` | Use compose screen | Interactive posting |
| `toot timeline` | Home screen | Enhanced timeline |
| `toot notifications` | Notifications screen | Filtered notifications |
| `toot search "query"` | Command palette | Fuzzy search |

### Keyboard Shortcuts

| Action | toot | tootles |
|--------|------|---------|
| Quit | `q` | `Ctrl+Q` |
| Refresh | `r` | `Ctrl+R` |
| Compose | `c` | `C` or `Ctrl+N` |
| Search | `/` | `Ctrl+P` |
| Home | `h` | `H` |
| Notifications | `n` | `N` |
| Explore | - | `E` |
| Bookmarks | - | `B` |
| Favorites | - | `F` |

## Troubleshooting

### Common Migration Issues

#### 1. Authentication Errors

**Problem**: "Invalid credentials" or "Unauthorized" errors

**Solution**:
1. Verify your `instance_url` is correct (include `https://`)
2. Check your `access_token` is valid
3. Generate a new token if needed:
   - Go to your instance's settings
   - Navigate to Development → Applications
   - Create new application or regenerate token

#### 2. Configuration Not Found

**Problem**: tootles doesn't find your configuration

**Solution**:
1. Ensure config file exists: `~/.config/tootles/config.toml`
2. Check file permissions are readable
3. Run with custom config: `tootles --config /path/to/config.toml`

#### 3. Theme Issues

**Problem**: Theme doesn't load or looks broken

**Solution**:
1. Reset to default theme: Set `theme = "default"` in config
2. Check theme file exists in `~/.config/tootles/themes/`
3. Validate theme CSS syntax

#### 4. Performance Issues

**Problem**: Slow loading or high memory usage

**Solution**:
1. Reduce `timeline_limit` in config
2. Disable streaming: `enable_streaming = false`
3. Reduce `cache_size` setting

### Getting Help

If you encounter issues:

1. **Check logs**: tootles logs to `~/.config/tootles/logs/`
2. **GitHub Issues**: Report bugs at [tootles repository](https://github.com/tootles-dev/tootles/issues)
3. **Community**: Join discussions in project forums

## Advanced Migration

### Custom Scripts

If you have scripts using toot commands, you can:

1. **Keep toot installed** alongside tootles for scripts
2. **Migrate to tootles API** (when available)
3. **Use tootles CLI mode** for automation

### Multiple Accounts

tootles currently supports one account per configuration. For multiple accounts:

1. Create separate config files:
   ```bash
   tootles --config ~/.config/tootles/account1.toml
   tootles --config ~/.config/tootles/account2.toml
   ```

2. Use shell aliases:
   ```bash
   alias tootles1='tootles --config ~/.config/tootles/account1.toml'
   alias tootles2='tootles --config ~/.config/tootles/account2.toml'
   ```

### Data Migration

tootles doesn't automatically import:
- **Drafts**: Copy manually if needed
- **Custom settings**: Reconfigure in tootles
- **Cached data**: Will rebuild automatically

## Next Steps

After successful migration:

1. **Explore themes**: Try built-in themes or create custom ones
2. **Learn shortcuts**: Master the keyboard navigation
3. **Use command palette**: Press `Ctrl+P` for quick actions
4. **Contribute**: Share themes or report issues

## Rollback Plan

If you need to return to toot:

1. **Keep toot installed**: Don't uninstall during migration
2. **Backup configs**: Save both toot and tootles configurations
3. **Test thoroughly**: Ensure tootles meets your needs before fully switching

The original toot remains functional and can be used alongside tootles.