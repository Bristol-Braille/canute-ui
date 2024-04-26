from ..state import state


# create a function to call when the button is pressed
# (otherwise the function call happens immediately)
def select_language(index):
    return lambda: state.app.languages.select_language(index)


buttons = {
    'single': {
        'L': state.app.close_menu,
        '2': select_language(0),
        '3': select_language(1),
        '4': select_language(2),
        '5': select_language(3),
        '6': select_language(4),
        '7': select_language(5),
        '8': select_language(6),
        '9': select_language(7),
        '<': state.app.previous_page,
        '>': state.app.next_page,
        'R': state.app.help_menu.toggle
    },
    'long': {
        'L': state.app.close_menu,
        '2': select_language(0),
        '3': select_language(1),
        '4': select_language(2),
        '5': select_language(3),
        '6': select_language(4),
        '7': select_language(5),
        '8': select_language(6),
        '9': select_language(7),
        '<': state.app.previous_page,
        '>': state.app.next_page,
        'R': state.app.help_menu.toggle,
        'X': state.hardware.reset_display
    }
}
