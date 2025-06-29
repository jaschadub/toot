# Contributing to Tootles

Thank you for your interest in contributing to tootles! This guide covers everything you need to know to contribute effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Contributions](#code-contributions)
4. [Theme Contributions](#theme-contributions)
5. [Documentation](#documentation)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Pull Request Process](#pull-request-process)
9. [Community Guidelines](#community-guidelines)

## Getting Started

### Ways to Contribute

- **🐛 Bug Reports**: Report issues and bugs
- **✨ Feature Requests**: Suggest new features
- **💻 Code**: Fix bugs, implement features
- **🎨 Themes**: Create and share custom themes
- **📚 Documentation**: Improve guides and docs
- **🧪 Testing**: Write tests, test features
- **💬 Community**: Help other users, answer questions

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Read the documentation** to understand the project
3. **Join discussions** to understand project direction
4. **Start small** with good first issues

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Text editor or IDE

### Clone and Setup

```bash
# Fork the repository on GitHub first
git clone https://github.com/YOUR_USERNAME/tootles.git
cd tootles

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The development setup includes:

- **pytest**: Testing framework
- **ruff**: Fast Python linter
- **black**: Code formatter
- **bandit**: Security linter
- **mypy**: Type checking
- **textual-dev**: Textual development tools

### Running Tootles in Development

```bash
# Run from source
python -m tootles.cli.main

# Or use the installed command
tootles

# Run with debug mode
TEXTUAL_DEBUG=1 tootles
```

### Project Structure

```
tootles/
├── tootles/                 # Main package
│   ├── __init__.py
│   ├── main.py             # Application entry point
│   ├── api/                # Mastodon API client
│   ├── cli/                # CLI interface
│   ├── config/             # Configuration management
│   ├── screens/            # UI screens
│   ├── themes/             # Theme management
│   └── widgets/            # UI widgets
├── tests/                  # Test suite
├── docs/                   # Documentation
└── themes-community/       # Community themes
```

## Code Contributions

### Finding Issues to Work On

1. **Good First Issues**: Look for `good-first-issue` label
2. **Help Wanted**: Check `help-wanted` label
3. **Bug Reports**: Fix reported bugs
4. **Feature Requests**: Implement requested features

### Development Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

2. **Make your changes** following code style guidelines

3. **Write tests** for new functionality

4. **Run the test suite**:
   ```bash
   pytest
   ```

5. **Run linting and formatting**:
   ```bash
   ruff check .
   black .
   bandit -r tootles/
   ```

6. **Test manually** with your changes

7. **Commit your changes** with clear messages

8. **Push and create a pull request**

### Code Guidelines

#### Python Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all functions
- Write **docstrings** for public methods
- Keep functions **focused and small**
- Use **meaningful variable names**

#### Example Code Style

```python
from typing import List, Optional
from textual.widget import Widget

class StatusWidget(Widget):
    """Widget for displaying a single Mastodon status.
    
    Args:
        status: The Status object to display
        app_ref: Reference to the main application
    """
    
    def __init__(self, status: Status, app_ref: "TootlesApp") -> None:
        super().__init__()
        self.status = status
        self.app_ref = app_ref
    
    async def handle_favorite(self) -> None:
        """Handle favorite/unfavorite of status."""
        try:
            if self.status.favourited:
                await self.app_ref.api_client.unfavorite_status(self.status.id)
                self.status.favourited = False
            else:
                await self.app_ref.api_client.favorite_status(self.status.id)
                self.status.favourited = True
                
            self.update_action_buttons()
            
        except Exception as e:
            self.app.notify(f"Failed to favorite: {e}", severity="error")
```

#### Textual Widget Guidelines

- **Extend base classes** when appropriate
- **Define DEFAULT_CSS** for styling
- **Use semantic CSS class names**
- **Handle focus properly**
- **Implement error handling**

```python
class MyWidget(Widget):
    """Custom widget with proper structure."""
    
    DEFAULT_CSS = """
    MyWidget {
        height: auto;
        background: $surface;
        border: solid $border;
    }
    
    MyWidget:focus {
        border-color: $primary;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = True
    
    def compose(self) -> ComposeResult:
        """Compose the widget layout."""
        yield Label("Widget content")
    
    def on_mount(self) -> None:
        """Handle widget mounting."""
        pass
```

### API Integration

When working with the Mastodon API:

- **Use async/await** consistently
- **Handle rate limiting** gracefully
- **Implement proper error handling**
- **Cache responses** when appropriate
- **Respect user privacy**

```python
async def get_timeline(self, timeline_type: str, **params) -> List[Status]:
    """Get timeline with proper error handling."""
    try:
        response = await self.session.get(
            f"{self.instance_url}/api/v1/timelines/{timeline_type}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        
        data = await response.json()
        return [Status.from_dict(item) for item in data]
        
    except aiohttp.ClientError as e:
        raise MastodonAPIError(f"Network error: {e}")
    except Exception as e:
        raise MastodonAPIError(f"Unexpected error: {e}")
```

## Theme Contributions

### Creating Themes

1. **Use the template**:
   ```bash
   tootles --export-template ~/.config/tootles/themes/my-theme.css
   ```

2. **Follow theme guidelines**:
   - Include all required selectors
   - Use consistent color relationships
   - Ensure good contrast ratios
   - Test with different content

3. **Document your theme**:
   ```css
   /* Theme Name: Cyberpunk Neon
    * Author: Your Name <email@example.com>
    * Description: A vibrant cyberpunk-inspired theme with neon accents
    * Version: 1.0
    * License: MIT
    * Inspired by: Cyberpunk 2077 color palette
    */
   ```

### Theme Submission Process

1. **Create theme directory**:
   ```
   themes-community/themes/your-theme-name/
   ├── theme.css          # Main theme file
   ├── README.md          # Theme description
   └── preview.png        # Optional preview image
   ```

2. **Test thoroughly**:
   - All screens and components
   - Different content types
   - Accessibility (contrast, focus)

3. **Submit pull request** with:
   - Clear description
   - Preview images
   - Testing notes

### Theme Quality Standards

- **Accessibility**: Minimum 4.5:1 contrast ratio
- **Consistency**: Coherent color relationships
- **Completeness**: All required selectors styled
- **Documentation**: Clear description and credits
- **Originality**: Unique and distinctive design

## Documentation

### Types of Documentation

- **User Guides**: Help users accomplish tasks
- **API Documentation**: Reference for developers
- **Theme Guides**: Help theme creators
- **Architecture Docs**: Technical implementation details

### Documentation Style

- **Clear and concise** language
- **Step-by-step instructions** for procedures
- **Code examples** for technical content
- **Screenshots or ASCII art** for visual elements
- **Cross-references** to related sections

### Writing Guidelines

1. **Use active voice** when possible
2. **Write for your audience** (users vs developers)
3. **Include practical examples**
4. **Keep it up to date** with code changes
5. **Test instructions** by following them

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=tootles

# Run with verbose output
pytest -v
```

### Writing Tests

#### Unit Tests

```python
import pytest
from tootles.config.schema import TootlesConfig

def test_config_validation():
    """Test configuration validation."""
    config = TootlesConfig()
    
    # Test valid configuration
    config.timeline_limit = 50
    config.validate()  # Should not raise
    
    # Test invalid configuration
    config.timeline_limit = -1
    with pytest.raises(ValueError):
        config.validate()
```

#### Widget Tests

```python
import pytest
from textual.app import App
from tootles.widgets.status import StatusWidget
from tootles.api.models import Status, Account

@pytest.fixture
def sample_status():
    """Create a sample status for testing."""
    account = Account(
        id="1",
        username="testuser",
        acct="testuser@example.com",
        display_name="Test User",
        # ... other required fields
    )
    
    return Status(
        id="1",
        content="Test status content",
        account=account,
        # ... other required fields
    )

async def test_status_widget_creation(sample_status):
    """Test status widget creation."""
    app = App()
    widget = StatusWidget(sample_status, app)
    
    assert widget.status == sample_status
    assert widget.app_ref == app
```

### Test Guidelines

- **Test public interfaces** not implementation details
- **Use descriptive test names** that explain what's being tested
- **Include edge cases** and error conditions
- **Mock external dependencies** (API calls, file system)
- **Keep tests fast** and independent

## Code Style

### Automated Formatting

We use automated tools to maintain consistent code style:

```bash
# Format code
black .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check . --fix

# Type checking
mypy tootles/

# Security scanning
bandit -r tootles/
```

### Pre-commit Hooks

Pre-commit hooks automatically run checks before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: [-r, tootles/]
```

### Import Organization

```python
# Standard library imports
import asyncio
import re
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import aiohttp
from textual.app import ComposeResult
from textual.widget import Widget

# Local imports
from tootles.api.models import Status
from tootles.config.manager import ConfigManager
```

### Error Handling

```python
# Good: Specific exception handling
try:
    result = await api_call()
except aiohttp.ClientError as e:
    logger.error(f"Network error: {e}")
    raise APIError("Failed to connect to server")
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise ValidationError("Invalid response format")

# Bad: Catching all exceptions
try:
    result = await api_call()
except Exception:
    pass  # Silent failure
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
   ```bash
   pytest
   ruff check .
   black --check .
   bandit -r tootles/
   ```

2. **Update documentation** if needed

3. **Add changelog entry** for user-facing changes

4. **Test manually** with your changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Theme contribution
- [ ] Refactoring

## Testing
- [ ] Tests pass
- [ ] Manual testing completed
- [ ] New tests added (if applicable)

## Screenshots
Include screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** on different platforms
4. **Documentation review** if applicable
5. **Approval and merge**

### After Merge

- **Monitor for issues** after merge
- **Respond to feedback** from users
- **Follow up** on related issues

## Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Welcome newcomers** and help them learn
- **Give constructive feedback**
- **Focus on the code**, not the person
- **Assume good intentions**

### Communication

- **Use clear, descriptive titles** for issues and PRs
- **Provide context** and examples
- **Be patient** with responses
- **Search existing issues** before creating new ones
- **Follow up** on your contributions

### Getting Help

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Discord/Matrix**: Real-time chat (if available)
- **Documentation**: Check existing guides first

## Recognition

Contributors are recognized through:

- **Contributors list** in README
- **Changelog mentions** for significant contributions
- **GitHub contributor graphs**
- **Community highlights** for exceptional contributions

## Questions?

If you have questions about contributing:

1. **Check the documentation** first
2. **Search existing issues** and discussions
3. **Ask in GitHub Discussions**
4. **Create an issue** for specific problems

Thank you for contributing to tootles! 🐘✨
