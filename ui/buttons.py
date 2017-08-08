import logging
import asyncio
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
    'system_menu': {
        'single': {
            '>': actions.next_page(),
            '<': actions.previous_page(),
            'L': actions.close_menu(),
            'R': actions.reset_display('start')
        }
    }
}


for i, item in enumerate(system_menu):
    action = system_menu[item]
    bindings['system_menu']['single'][str(i + 2)] = action


prev_buttons = {}
@asyncio.coroutine
def check(driver, state, store):
    global prev_buttons
    buttons = driver.get_buttons()
    location = state['app']['location']
    for key in buttons:
        up_or_down = buttons[key]
        if up_or_down == 'down':
            prev_buttons[key] = datetime.now()
        elif up_or_down == 'up' and key in prev_buttons:
            diff = (datetime.now() - prev_buttons[key]).total_seconds()
            del prev_buttons[key]

            press_type = 'single'
            if diff > 1:
                press_type = 'long'

            try:
                action = bindings[location][press_type][key]
            except KeyError:
                log.debug('no binding for key {}, {} press'.format(key, press_type))
            else:
                yield from store.dispatch(action)
