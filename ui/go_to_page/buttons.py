from functools import partial
from ..actions import actions

go_to_page_buttons = {
    'single': {
        'L': actions.close_menu,
        '1': partial(actions.go_to_page_enter_number, 1),
        '2': partial(actions.go_to_page_enter_number, 2),
        '3': partial(actions.go_to_page_enter_number, 3),
        '4': partial(actions.go_to_page_enter_number, 4),
        '5': partial(actions.go_to_page_enter_number, 5),
        '6': partial(actions.go_to_page_enter_number, 6),
        '7': partial(actions.go_to_page_enter_number, 7),
        '8': partial(actions.go_to_page_enter_number, 8),
        '9': partial(actions.go_to_page_enter_number, 9),
        'X': partial(actions.go_to_page_enter_number, 0),
        '<': actions.go_to_page_delete,
        '>': actions.go_to_page_confirm,
    },
}
