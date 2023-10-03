from ..state import state


# create a function to call when the button is pressed
# (otherwise the function call happens immediately)
def go_to_book(number):
    return lambda: state.app.library.go_to_book(number)


library_buttons = {
    'single': {
        '2': go_to_book(0),
        '3': go_to_book(1),
        '4': go_to_book(2),
        '5': go_to_book(3),
        '6': go_to_book(4),
        '7': go_to_book(5),
        '8': go_to_book(6),
        '9': go_to_book(7),
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
        'R': state.app.help_menu.toggle,
    },
    'long': {
        '2': go_to_book(0),
        '3': go_to_book(1),
        '4': go_to_book(2),
        '5': go_to_book(3),
        '6': go_to_book(4),
        '7': go_to_book(5),
        '8': go_to_book(6),
        '9': go_to_book(7),
        '<': lambda: state.app.skip_pages(-5),
        '>': lambda: state.app.skip_pages(5),
        'L': state.app.close_menu,
        'R': state.app.help_menu.toggle,
        'X': state.hardware.reset_display
    },
}
