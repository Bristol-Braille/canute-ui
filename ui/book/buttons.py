
from ..actions import actions

book_buttons = {
    'single': {
        '2': actions.enter_go_to_page(),
        '3': actions.go_to_start(),
        '4': actions.go_to_end(),
        '5': actions.insert_bookmark(),
        '6': actions.go_to_bookmarks_menu(),
        '8': actions.go_to_library(),
        '9': actions.go_to_system_menu(),
        'R': actions.reset_display('start'),
        '>': actions.next_page(),
        '<': actions.previous_page(),
        'L': actions.toggle_home_menu(),
    }
}
