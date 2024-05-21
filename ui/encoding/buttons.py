from ..state import state


# create a function to call when the button is pressed
# (otherwise the function call happens immediately)
def select_encoding(index):
    return lambda: state.app.encoding.select_encoding(index)


buttons = {
    'single': {
        'L': state.app.close_menu,
        '2': select_encoding(0),
        '3': select_encoding(1),
        '4': select_encoding(2),
        '5': select_encoding(3),
        '6': select_encoding(4),
        '7': select_encoding(5),
        '8': select_encoding(6),
        '9': select_encoding(7),
        '<': state.app.previous_page,
        '>': state.app.next_page,
        'R': state.app.help_menu.toggle
    },
    'long': {
        'L': state.app.close_menu,
        '2': select_encoding(0),
        '3': select_encoding(1),
        '4': select_encoding(2),
        '5': select_encoding(3),
        '6': select_encoding(4),
        '7': select_encoding(5),
        '8': select_encoding(6),
        '9': select_encoding(7),
        '<': state.app.previous_page,
        '>': state.app.next_page,
        'R': state.app.help_menu.toggle,
        'X': state.hardware.reset_display
    }
}
