from ..actions import actions

bookmarks_buttons = {
    'single': {
        'L': actions.close_menu(),
        '2': actions.go_to_bookmark(0),
        '3': actions.go_to_bookmark(1),
        '4': actions.go_to_bookmark(2),
        '5': actions.go_to_bookmark(3),
        '6': actions.go_to_bookmark(4),
        '7': actions.go_to_bookmark(5),
        '8': actions.go_to_bookmark(6),
        '9': actions.go_to_bookmark(7),
        '<': actions.previous_page(),
        '>': actions.next_page(),
        'R': actions.reset_display('start'),
    },
    'long': {
        'L': actions.close_menu(),
        '2': actions.delete_bookmark(0),
        '3': actions.delete_bookmark(1),
        '4': actions.delete_bookmark(2),
        '5': actions.delete_bookmark(3),
        '6': actions.delete_bookmark(4),
        '7': actions.delete_bookmark(5),
        '8': actions.delete_bookmark(6),
        '9': actions.delete_bookmark(7),
        '<': actions.skip_pages(-5),
        '>': actions.skip_pages(5),
        'R': actions.reset_display('start'),
    },
}
