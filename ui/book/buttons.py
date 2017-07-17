from functools import partial

from ..actions import actions

book_buttons = {
    'single': {
        '1': actions.go_to_start,
        '2': partial(actions.skip_pages, -10),
        '3': partial(actions.skip_pages, 10),
        '>': actions.next_page,
        '<': actions.previous_page,
        'L': actions.go_to_library,
        'R': partial(actions.reset_display, 'start')
    }
}
