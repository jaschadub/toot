# Theme Development Guide

This guide covers creating custom themes for tootles, from basic color changes to advanced CSS customizations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Theme Structure](#theme-structure)
3. [CSS Variables Reference](#css-variables-reference)
4. [Component Styling](#component-styling)
5. [Creating Your First Theme](#creating-your-first-theme)
6. [Advanced Techniques](#advanced-techniques)
7. [Testing and Validation](#testing-and-validation)
8. [Contributing Themes](#contributing-themes)

## Getting Started

### Prerequisites

- Basic understanding of CSS
- tootles installed and configured
- Text editor for CSS editing

### Theme Directory

Themes are stored in:
```
~/.config/tootles/themes/
```

Create this directory if it doesn't exist:
```bash
mkdir -p ~/.config/tootles/themes/
```

### Quick Start

1. **Copy the template**:
   ```bash
   tootles --export-template ~/.config/tootles/themes/my-theme.css
   ```

2. **Edit the theme**:
   ```bash
   nano ~/.config/tootles/themes/my-theme.css
   ```

3. **Apply the theme**:
   Set `theme = "my-theme"` in `~/.config/tootles/config.toml`

4. **Restart tootles** to see changes

## Theme Structure

### Basic Theme File

```css
/* Theme Name: My Custom Theme
 * Author: Your Name
 * Description: A beautiful custom theme for tootles
 * Version: 1.0
 */

/* Required selectors - must be present */
.app-container { /* Main application background */ }
.status-item { /* Individual status/toot styling */ }
.timeline-widget { /* Timeline container */ }
.compose-widget { /* Compose interface */ }
.button { /* Button styling */ }
.input-field { /* Input field styling */ }

/* Optional selectors for enhanced customization */
.sidebar-navigation { /* Navigation sidebar */ }
.status-header { /* Status author info */ }
.status-content { /* Status text content */ }
/* ... more selectors ... */
```

### Required Selectors

These selectors **must** be present for theme validation:

| Selector | Purpose |
|----------|---------|
| `.app-container` | Main application background and text color |
| `.status-item` | Individual status/toot appearance |
| `.timeline-widget` | Timeline container styling |
| `.compose-widget` | Compose interface styling |
| `.button` | Button appearance |
| `.input-field` | Input field styling |

## CSS Variables Reference

### Color Variables

Tootles supports CSS variables for consistent theming:

```css
/* Primary colors */
$background      /* Main background color */
$surface         /* Widget/container background */
$primary         /* Primary accent color */
$accent          /* Secondary accent color */

/* Text colors */
$text            /* Main text color */
$text-muted      /* Secondary text color */
$text-disabled   /* Disabled text color */
$text-inverse    /* Text on colored backgrounds */

/* State colors */
$error           /* Error/danger color */
$warning         /* Warning color */
$success         /* Success color */
$border          /* Border color */

/* Surface variations */
$surface-lighten-1   /* Slightly lighter surface */
$surface-darken-1    /* Slightly darker surface */
$surface-darken-2    /* Much darker surface */
$primary-muted       /* Muted primary color */
$primary-lighten-1   /* Lighter primary color */
```

### Using Variables

```css
.my-widget {
    background: $surface;
    color: $text;
    border: solid $border;
}

.my-widget:hover {
    background: $surface-lighten-1;
    color: $primary;
}
```

## Component Styling

### Application Layout

```css
/* Main application container */
.app-container {
    background: #1a1a1a;
    color: #ffffff;
}

/* Screen containers */
.screen-container {
    background: #2a2a2a;
    border: solid #444444;
}

/* Navigation sidebar */
.sidebar-navigation {
    background: #2a2a2a;
    border-right: solid #444444;
    width: 20;
}
```

### Navigation Elements

```css
/* Navigation items */
.nav-item {
    padding: 1;
    margin: 0 1;
    background: transparent;
    color: #cccccc;
}

.nav-item:hover {
    background: #3a3a3a;
    color: #ffffff;
}

.nav-item--active {
    background: #0066cc;
    color: #ffffff;
}
```

### Status Display

```css
/* Status list container */
.status-list {
    background: #2a2a2a;
    border: solid #444444;
}

/* Individual status */
.status-item {
    padding: 1;
    margin-bottom: 1;
    background: #2a2a2a;
    border: solid #444444;
}

.status-item:hover {
    background: #3a3a3a;
}

.status-item--focused {
    border: solid #0066cc;
    background: #1a3a5a;
}

/* Status components */
.status-header {
    color: #cccccc;
    text-style: bold;
}

.status-content {
    color: #ffffff;
    margin: 1 0;
}

.status-actions {
    color: #cccccc;
    margin-top: 1;
}
```

### Interactive Elements

```css
/* Buttons */
.button {
    background: #0066cc;
    color: #ffffff;
    border: none;
    padding: 0 2;
}

.button:hover {
    background: #0052a3;
}

.button--secondary {
    background: #444444;
    color: #ffffff;
    border: solid #666666;
}

.button--danger {
    background: #cc3333;
    color: #ffffff;
}

/* Input fields */
.input-field {
    background: #3a3a3a;
    color: #ffffff;
    border: solid #666666;
    padding: 0 1;
}

.input-field:focus {
    border-color: #0066cc;
}
```

### Timeline Widget

```css
.timeline-widget {
    background: #2a2a2a;
    border: solid #444444;
    padding: 1;
}

.timeline-header {
    background: #3a3a3a;
    color: #ffffff;
    text-style: bold;
    padding: 1;
    border-bottom: solid #444444;
}

.timeline-loading {
    color: #cccccc;
    text-style: italic;
    text-align: center;
    padding: 2;
}

.timeline-error {
    color: #cc3333;
    text-style: bold;
    text-align: center;
    padding: 2;
}
```

### Compose Widget

```css
.compose-widget {
    background: #2a2a2a;
    border: solid #444444;
    padding: 1;
}

.compose-textarea {
    background: #1a1a1a;
    color: #ffffff;
    border: solid #666666;
    padding: 1;
    margin-bottom: 1;
    min-height: 6;
}

.compose-textarea:focus {
    border-color: #0066cc;
}

.compose-char-count {
    color: #cccccc;
    text-style: dim;
}

.compose-char-count--warning {
    color: #ffaa00;
    text-style: bold;
}

.compose-char-count--error {
    color: #cc3333;
    text-style: bold;
}
```

## Creating Your First Theme

### Step 1: Plan Your Theme

Choose your color palette:
- **Background colors**: Main background, widget backgrounds
- **Text colors**: Primary text, secondary text, disabled text
- **Accent colors**: Primary accent, success, warning, error
- **Border colors**: Subtle borders, focus indicators

### Step 2: Start with the Template

```bash
# Export the community template
tootles --export-template ~/.config/tootles/themes/my-theme.css
```

### Step 3: Customize Colors

Edit the template and replace the placeholder colors:

```css
/* Replace these colors with your palette */
.app-container {
    background: #your-background-color;
    color: #your-text-color;
}

.status-item {
    background: #your-surface-color;
    border: solid #your-border-color;
}

.button {
    background: #your-primary-color;
    color: #your-button-text-color;
}
```

### Step 4: Test Your Theme

1. Save the file
2. Update your config: `theme = "my-theme"`
3. Restart tootles
4. Check all screens and components

### Step 5: Refine and Polish

- Test with different content types
- Check readability in various lighting
- Ensure sufficient contrast
- Test focus indicators

## Advanced Techniques

### Color Schemes

#### Dark Theme Example
```css
.app-container {
    background: #0d1117;
    color: #f0f6fc;
}

.surface {
    background: #161b22;
    border: solid #30363d;
}

.primary {
    background: #238636;
    color: #ffffff;
}
```

#### Light Theme Example
```css
.app-container {
    background: #ffffff;
    color: #24292f;
}

.surface {
    background: #f6f8fa;
    border: solid #d0d7de;
}

.primary {
    background: #2da44e;
    color: #ffffff;
}
```

### Responsive Design

```css
/* Adjust for different terminal sizes */
.sidebar-navigation {
    width: 20;
    min-width: 15;
    max-width: 25;
}

.status-item {
    padding: 1;
    margin-bottom: 1;
}

/* Compact mode for smaller terminals */
@media (max-width: 80) {
    .sidebar-navigation {
        width: 15;
    }
    
    .status-item {
        padding: 0 1;
    }
}
```

### Animation and Transitions

```css
/* Smooth transitions */
.button {
    transition: background 0.2s ease;
}

.status-item {
    transition: background 0.1s ease, border-color 0.1s ease;
}

/* Focus animations */
.input-field:focus {
    border-color: #0066cc;
    transition: border-color 0.2s ease;
}
```

### Custom Scrollbars

```css
.scrollable {
    scrollbar-background: #2a2a2a;
    scrollbar-color: #666666;
    scrollbar-corner-color: #2a2a2a;
}

.scrollable:hover {
    scrollbar-color: #888888;
}
```

## Testing and Validation

### Manual Testing

Test your theme across all screens:

1. **Home Timeline**: Status display, interactions
2. **Notifications**: Different notification types
3. **Compose**: Text input, character counter
4. **Settings**: Form elements, buttons
5. **Command Palette**: Search interface

### Validation Checklist

- [ ] All required selectors present
- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Focus indicators visible
- [ ] Error states clearly distinguishable
- [ ] Readable in different lighting conditions
- [ ] No CSS syntax errors

### Automated Validation

```bash
# Validate theme syntax (when available)
tootles --validate-theme ~/.config/tootles/themes/my-theme.css
```

### Hot Reload for Development

Enable hot reload in your config:

```toml
enable_theme_hot_reload = true
```

Now changes to your theme file will automatically reload in tootles.

## Contributing Themes

### Preparing for Contribution

1. **Test thoroughly** across all components
2. **Document your theme**:
   ```css
   /* Theme Name: Cyberpunk Neon
    * Author: Your Name <email@example.com>
    * Description: A vibrant cyberpunk-inspired theme with neon accents
    * Version: 1.0
    * License: MIT
    * Inspired by: Cyberpunk 2077 color palette
    */
   ```

3. **Create a preview** (screenshot or ASCII art)
4. **Follow naming conventions**: `kebab-case-names.css`

### Submission Process

1. **Fork the repository**
2. **Add your theme** to `themes-community/themes/`
3. **Include documentation**:
   - Theme file with header comments
   - README.md with description and preview
   - Optional: preview.png screenshot

4. **Submit pull request** with:
   - Clear description
   - Preview images
   - Testing notes

### Theme Guidelines

- **Accessibility**: Ensure good contrast ratios
- **Consistency**: Use coherent color relationships
- **Documentation**: Include clear descriptions
- **Originality**: Create unique, distinctive themes
- **Quality**: Test thoroughly before submission

### Community Standards

- Respectful naming and descriptions
- No offensive or inappropriate content
- Credit inspirations and sources
- Follow project code of conduct

## Troubleshooting

### Common Issues

#### Theme Not Loading
- Check file exists in `~/.config/tootles/themes/`
- Verify filename matches config setting
- Check file permissions

#### CSS Syntax Errors
- Validate CSS syntax
- Check for unmatched braces `{}`
- Ensure proper property formatting

#### Colors Not Applying
- Verify selector names match exactly
- Check CSS specificity rules
- Ensure required selectors are present

#### Poor Readability
- Increase contrast ratios
- Test in different lighting
- Consider colorblind accessibility

### Debug Mode

Enable debug mode for theme development:

```toml
debug_mode = true
theme_debug = true
```

This provides additional logging and validation information.

## Resources

### Color Tools
- [Coolors.co](https://coolors.co/) - Color palette generator
- [Contrast Checker](https://webaim.org/resources/contrastchecker/) - Accessibility testing
- [Adobe Color](https://color.adobe.com/) - Color wheel and harmony

### Inspiration
- [Terminal themes](https://github.com/mbadolato/iTerm2-Color-Schemes)
- [VS Code themes](https://vscodethemes.com/)
- [Material Design](https://material.io/design/color/)

### Documentation
- [Textual CSS Guide](https://textual.textualize.io/guide/CSS/)
- [CSS Color Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/color)

## Examples

See the `themes-community/` directory for example themes and templates.

Happy theming! 🎨