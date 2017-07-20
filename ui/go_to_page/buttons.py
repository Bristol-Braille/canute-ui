from ..actions import actions

go_to_page_buttons = {
    'single': {
        'L': actions.close_menu,
        '1': lambda: actions.go_to_page_enter_number(1),
        '2': lambda: actions.go_to_page_enter_number(2),
        '3': lambda: actions.go_to_page_enter_number(3),
        '4': lambda: actions.go_to_page_enter_number(4),
        '5': lambda: actions.go_to_page_enter_number(5),
        '6': lambda: actions.go_to_page_enter_number(6),
        '7': lambda: actions.go_to_page_enter_number(7),
        '8': lambda: actions.go_to_page_enter_number(8),
        '9': lambda: actions.go_to_page_enter_number(9),
        'X': lambda: actions.go_to_page_enter_number(0),
        '<': actions.go_to_page_delete,
        '>': actions.go_to_page_confirm,
        'R': lambda: actions.reset_display('start'),
    },
}
