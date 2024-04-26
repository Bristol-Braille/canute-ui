from ..state import state


# create a function to call when the button is pressed
# (otherwise the function call happens immediately)
def library_action(number):
    return lambda: state.app.library.action(number - 1)


buttons = {
    'single': {
        '2': library_action(2),
        '3': library_action(3),
        '4': library_action(4),
        '5': library_action(5),
        '6': library_action(6),
        '7': library_action(7),
        '8': library_action(8),
        '9': library_action(9),
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
        'R': state.app.help_menu.toggle,
    },
    'long': {
        '2': library_action(2),
        '3': library_action(3),
        '4': library_action(4),
        '5': library_action(5),
        '6': library_action(6),
        '7': library_action(7),
        '8': library_action(8),
        '9': library_action(9),
        '<': lambda: state.app.skip_pages(-5),
        '>': lambda: state.app.skip_pages(5),
        'L': state.app.close_menu,
        'R': state.app.help_menu.toggle,
        'X': state.hardware.reset_display
    },
}
