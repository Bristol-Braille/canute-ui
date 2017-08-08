from ..actions import actions

library_buttons = {
    'single': {
        '>': actions.next_page(),
        '<': actions.previous_page(),
        '2': actions.go_to_book(0),
        '3': actions.go_to_book(1),
        '4': actions.go_to_book(2),
        '5': actions.go_to_book(3),
        '6': actions.go_to_book(4),
        '7': actions.go_to_book(5),
        '8': actions.go_to_book(6),
        '9': actions.go_to_book(7),
        'L': actions.close_menu(),
        'R': actions.reset_display('start')
    },
    'single': {
        '>': actions.next_page(),
        '<': actions.previous_page(),
        '2': actions.go_to_book(0),
        '3': actions.go_to_book(1),
        '4': actions.go_to_book(2),
        '5': actions.go_to_book(3),
        '6': actions.go_to_book(4),
        '7': actions.go_to_book(5),
        '8': actions.go_to_book(6),
        '9': actions.go_to_book(7),
        '<': actions.skip_pages(-5),
        '>': actions.skip_pages(5),
        'L': actions.close_menu(),
        'R': actions.reset_display('start')
    },
}
