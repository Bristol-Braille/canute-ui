from ..actions import actions

language_buttons = {
    'single': {
        'L': actions.close_menu(),
        '2': actions.select_language(0),
        '3': actions.select_language(1),
        '4': actions.select_language(2),
        '5': actions.select_language(3),
        '6': actions.select_language(4),
        '7': actions.select_language(5),
        '8': actions.select_language(6),
        '9': actions.select_language(7),
        '<': actions.previous_page(),
        '>': actions.next_page(),
        'R': actions.toggle_help_menu(),
    },
    'long': {
        'L': actions.close_menu(),
        '2': actions.select_language(0),
        '3': actions.select_language(1),
        '4': actions.select_language(2),
        '5': actions.select_language(3),
        '6': actions.select_language(4),
        '7': actions.select_language(5),
        '8': actions.select_language(6),
        '9': actions.select_language(7),
        '<': actions.previous_page(),
        '>': actions.next_page(),
        'R': actions.toggle_help_menu(),
        'X': actions.reset_display('start')
    }
}
