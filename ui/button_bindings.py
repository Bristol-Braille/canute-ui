from functools import partial

from actions import actions

button_bindings = {
    'library': {
        'single': {
            '>' : actions.next_page,
            '<' : actions.previous_page,
            '1' : partial(actions.go_to_book, 0),
            '2' : partial(actions.go_to_book, 1),
            '3' : partial(actions.go_to_book, 2),
            '4' : partial(actions.go_to_book, 3),
            '5' : partial(actions.go_to_book, 4),
            '6' : partial(actions.go_to_book, 5),
            '7' : partial(actions.go_to_book, 6),
            '8' : partial(actions.go_to_book, 7),
            '9' : partial(actions.go_to_book, 8),
            'L' : actions.go_to_menu,
        }
    },
    'book': {
        'single': {
            '>' : actions.next_page,
            '<' : actions.previous_page,
            'L' : actions.go_to_library,
        }
    },
    'menu': {
        'single': {
            '>' : actions.next_page,
            '<' : actions.previous_page,
            'L' : actions.go_to_library,
            '1' : actions.replace_library,
            '2' : actions.replace_library,
        }
    }
}

