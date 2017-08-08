from ..actions import actions

bookmarks_buttons = {
    'single': {
        'L': actions.close_menu(),
        '1': actions.go_to_bookmark(0),
        '2': actions.go_to_bookmark(1),
        '3': actions.go_to_bookmark(2),
        '4': actions.go_to_bookmark(3),
        '5': actions.go_to_bookmark(4),
        '6': actions.go_to_bookmark(5),
        '7': actions.go_to_bookmark(6),
        '8': actions.go_to_bookmark(7),
        '9': actions.go_to_bookmark(8),
        '<': actions.previous_page(),
        '>': actions.next_page(),
        'R': actions.reset_display('start'),
    },
    'long': {
        'L': actions.close_menu(),
        '1': actions.delete_bookmark(0),
        '2': actions.delete_bookmark(1),
        '3': actions.delete_bookmark(2),
        '4': actions.delete_bookmark(3),
        '5': actions.delete_bookmark(4),
        '6': actions.delete_bookmark(5),
        '7': actions.delete_bookmark(6),
        '8': actions.delete_bookmark(7),
        '9': actions.delete_bookmark(8),
        '<': actions.previous_page(),
        '>': actions.next_page(),
        'R': actions.reset_display('start'),
    },
}
