from ..actions import actions

bookmarks_buttons = {
    'single': {
        'L': actions.close_menu(),
        # '1': queue_key_press(1),
        # '2': queue_key_press(2),
        # '3': queue_key_press(3),
        # '4': queue_key_press(4),
        # '5': queue_key_press(5),
        # '6': queue_key_press(6),
        # '7': queue_key_press(7),
        # '8': queue_key_press(8),
        # '9': queue_key_press(9),
        # 'X': queue_key_press(0),
        # '<': queue_key_press('<'),
        # '>': actions.go_to_page_confirm(),
        'R': actions.reset_display('start'),
    },
}
