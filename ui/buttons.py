import logging
from datetime import datetime
from .state import state
from .system_menu.system_menu import system_menu
from .library.buttons import library_buttons
from .book.buttons import book_buttons
from .go_to_page.buttons import go_to_page_buttons
from .bookmarks.buttons import bookmarks_buttons
from .language.buttons import language_buttons


log = logging.getLogger(__name__)


bindings = {
    'library': library_buttons,
    'book': book_buttons,
    'go_to_page': go_to_page_buttons,
    'bookmarks_menu': bookmarks_buttons,
    'language': language_buttons,
    'help_menu': {
        'single': {
            'L': state.app.close_menu,
            '>': state.app.next_page,
            '<': state.app.previous_page,
            'R': state.app.help_menu.toggle,
        },
        'long': {
            'L': state.app.close_menu,
            '>': state.app.next_page,
            '<': state.app.previous_page,
            'R': state.app.help_menu.toggle,
            'X': state.hardware.reset_display,
        },
    },
    'system_menu': {
        'single': {
            'R': state.app.help_menu.toggle,
            '>': state.app.next_page,
            '<': state.app.previous_page,
            'L': state.app.close_menu,
        },
        'long': {
            'R': state.app.help_menu.toggle,
            '>': state.app.next_page,
            '<': state.app.previous_page,
            'L': state.app.close_menu,
            'X': state.hardware.reset_display,
        },
    }
}

sys_menu = system_menu()

for i, item in enumerate(sys_menu):
    action = sys_menu[item]
    bindings['system_menu']['single'][str(i + 2)] = action


async def dispatch_button(key, press_type, state):
    location = state.app.location_or_help_menu
    try:
        action = bindings[location][press_type][key]
    except KeyError:
        log.debug('no binding for key {}, {} press'.format(key, press_type))
    else:
        action()


prev_buttons = {}
long_buttons = {}


async def check(driver, state):
    # this is a hack for now until we change the protocol, we read the buttons
    # twice so we don't miss the release of short presses
    for _ in range(2):
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
                    await dispatch_button(key, 'single', state)

        for key in prev_buttons:
            diff = (datetime.now() - prev_buttons[key]).total_seconds()
            if diff > 0.5:
                prev_buttons[key] = datetime.now()
                long_buttons[key] = True
                await dispatch_button(key, 'long', state)
