from urwid.command_map import (
    CURSOR_DOWN,
    CURSOR_LEFT,
    CURSOR_RIGHT,
    CURSOR_UP,
    command_map,
)

# Add movement using h/j/k/l to default command map
command_map._command.update({
    'k': CURSOR_UP,
    'j': CURSOR_DOWN,
    'h': CURSOR_LEFT,
    'l': CURSOR_RIGHT,
})
