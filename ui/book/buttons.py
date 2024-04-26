from ..state import state

buttons = {
    'single': {
        '2': state.app.user.enter_go_to_page,
        '5': state.app.user.insert_bookmark,
        '6': state.app.go_to_bookmarks_menu,
        '8': state.app.go_to_system_menu,
        '9': state.app.go_to_library,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.user.toggle_home_menu,
        'R': state.app.help_menu.toggle,
    },
    'long': {
        '2': state.app.user.enter_go_to_page,
        '5': state.app.user.insert_bookmark,
        '6': state.app.go_to_bookmarks_menu,
        '8': state.app.go_to_system_menu,
        '9': state.app.go_to_library,
        '<': lambda: state.app.skip_pages(-3),
        '>': lambda: state.app.skip_pages(3),
        'L': state.app.user.toggle_home_menu,
        'R': state.app.help_menu.toggle,
        'X': state.hardware.reset_display
    },
}
