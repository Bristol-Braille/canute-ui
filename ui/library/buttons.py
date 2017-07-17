from functools import partial

from ..actions import actions

library_buttons = {
    'single': {
        '>': actions.next_page,
        '<': actions.previous_page,
        '2': partial(actions.go_to_book, 0),
        '3': partial(actions.go_to_book, 1),
        '4': partial(actions.go_to_book, 2),
        '5': partial(actions.go_to_book, 3),
        '6': partial(actions.go_to_book, 4),
        '7': partial(actions.go_to_book, 5),
        '8': partial(actions.go_to_book, 6),
        '9': partial(actions.go_to_book, 7),
        'L': actions.go_to_system_menu,
        'R': partial(actions.reset_display, 'start')
    }
}
