from functools import partial

from .actions import actions
from .menu import menu


button_bindings = {
    'library': {
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
            'L': actions.go_to_menu,
        }
    },
    'book': {
        'single': {
            '1': actions.go_to_start,
            '2': partial(actions.skip_pages, -10),
            '3': partial(actions.skip_pages, 10),
            '>': actions.next_page,
            '<': actions.previous_page,
            'L': actions.go_to_library,
        }
    },
    'menu': {
        'single': {
            '>': actions.next_page,
            '<': actions.previous_page,
            'L': actions.go_to_library,
        }
    }
}

for i, item in enumerate(menu):
    action = menu[item]
    button_bindings['menu']['single'][str(i + 2)] = action
