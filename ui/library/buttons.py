from ..actions import actions

library_buttons = {
    'single': {
        '>': actions.next_page,
        '<': actions.previous_page,
        '2': lambda: actions.go_to_book(0),
        '3': lambda: actions.go_to_book(1),
        '4': lambda: actions.go_to_book(2),
        '5': lambda: actions.go_to_book(3),
        '6': lambda: actions.go_to_book(4),
        '7': lambda: actions.go_to_book(5),
        '8': lambda: actions.go_to_book(6),
        '9': lambda: actions.go_to_book(7),
        'L': actions.close_menu,
        'R': lambda: actions.reset_display('start')
    }
}
