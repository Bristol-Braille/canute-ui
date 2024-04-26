from ..state import state

buttons = {
    'single': {
        '2': state.app.shutdown,
        '3': state.app.go_to_language_menu,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
    },
    'long': {
        '2': state.app.shutdown,
        '3': state.app.go_to_language_menu,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
        'X': state.hardware.reset_display,
    },
}
