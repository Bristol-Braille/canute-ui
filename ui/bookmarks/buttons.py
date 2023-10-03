from ..state import state

# create functions to call when the button is pressed
# (otherwise the function call happens immediately)
def go_to_bookmark(number):
    return lambda: state.app.bookmarks_menu.go_to_bookmark(number)

def delete_bookmark(number):
    return lambda: state.app.bookmarks_menu.delete_bookmark(number)

bookmarks_buttons = {
    'single': {
        'L': state.app.close_menu,
        '2': go_to_bookmark(0),
        '3': go_to_bookmark(1),
        '4': go_to_bookmark(2),
        '5': go_to_bookmark(3),
        '6': go_to_bookmark(4),
        '7': go_to_bookmark(5),
        '8': go_to_bookmark(6),
        '9': go_to_bookmark(7),
        '<': state.app.previous_page,
        '>': state.app.next_page,
        'R': state.app.help_menu.toggle,
    },
    'long': {
        'L': state.app.close_menu,
        '2': delete_bookmark(0),
        '3': delete_bookmark(1),
        '4': delete_bookmark(2),
        '5': delete_bookmark(3),
        '6': delete_bookmark(4),
        '7': delete_bookmark(5),
        '8': delete_bookmark(6),
        '9': delete_bookmark(7),
        '<': lambda: state.app.skip_pages(-3),
        '>': lambda: state.app.skip_pages(3),
        'X': state.hardware.reset_display,
        'R': state.app.help_menu.toggle,
    },
}
