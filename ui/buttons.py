import logging
from datetime import datetime
from .actions import actions
from .system_menu.system_menu import system_menu
from .library.buttons import library_buttons
from .book.buttons import book_buttons
from .go_to_page.buttons import go_to_page_buttons
from .bookmarks.buttons import bookmarks_buttons


log = logging.getLogger(__name__)


bindings = {
    'library': library_buttons,
    'book': book_buttons,
    'go_to_page': go_to_page_buttons,
    'bookmarks_menu': bookmarks_buttons,
    'help_menu': {
        'single': {
            'L': actions.close_menu(),
            '>': actions.next_page(),
            '<': actions.previous_page(),
            'R': actions.toggle_help_menu(),
        },
        'long': {
            'L': actions.close_menu(),
            '>': actions.next_page(),
            '<': actions.previous_page(),
            'R': actions.toggle_help_menu(),
            'X': actions.reset_display('start'),
        },
    },
    'system_menu': {
        'single': {
            'R': actions.toggle_help_menu(),
            '>': actions.next_page(),
            '<': actions.previous_page(),
            'L': actions.close_menu(),
        },
        'long': {
            'R': actions.toggle_help_menu(),
            '>': actions.next_page(),
            '<': actions.previous_page(),
            'L': actions.close_menu(),
            'X': actions.reset_display('start'),
        },
    }
}


for i, item in enumerate(system_menu):
    action = system_menu[item]
    bindings['system_menu']['single'][str(i + 2)] = action


async def dispatch_button(key, press_type, state, dispatch):
    if state['help_menu']['visible']:
        location = 'help_menu'
    else:
        location = state['location']
    try:
        action = bindings[location][press_type][key]
    except KeyError:
        log.debug('no binding for key {}, {} press'.format(key, press_type))
    else:
        await dispatch(action)


prev_buttons = {}
long_buttons = {}


async def check(driver, state, dispatch):
    buttons = driver.get_buttons()
    for key in buttons:
        up_or_down = buttons[key]
        if up_or_down == 'down':
            prev_buttons[key] = datetime.now()
        elif up_or_down == 'up':
            if key in long_buttons:
                del long_buttons[key]
                del prev_buttons[key]
            else:
                if key in prev_buttons:
                    del prev_buttons[key]
                await dispatch_button(key, 'single', state, dispatch)

    for key in prev_buttons:
        diff = (datetime.now() - prev_buttons[key]).total_seconds()
        if diff > 0.5:
            prev_buttons[key] = datetime.now()
            long_buttons[key] = True
            await dispatch_button(key, 'long', state, dispatch)
