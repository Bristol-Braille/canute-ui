from ..actions import actions

go_to_page_buttons = {
    'single': {
        'L': actions.close_menu(),
        '1': actions.go_to_page_enter_number(1),
        '2': actions.go_to_page_enter_number(2),
        '3': actions.go_to_page_enter_number(3),
        '4': actions.go_to_page_enter_number(4),
        '5': actions.go_to_page_enter_number(5),
        '6': actions.go_to_page_enter_number(6),
        '7': actions.go_to_page_enter_number(7),
        '8': actions.go_to_page_enter_number(8),
        '9': actions.go_to_page_enter_number(9),
        'X': actions.go_to_page_enter_number(0),
        '<': actions.go_to_page_delete(),
        '>': actions.go_to_page_confirm(),
        'R': actions.reset_display('start'),
    },
}
