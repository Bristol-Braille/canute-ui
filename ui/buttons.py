import logging
from functools import partial
from .store import store
from .actions import actions
from .system_menu import system_menu
from .library.buttons import library_buttons
from .book.buttons import book_buttons


log = logging.getLogger(__name__)


bindings = {
    'library': library_buttons,
    'book': book_buttons,
    'system_menu': {
        'single': {
            '>': actions.next_page,
            '<': actions.previous_page,
            'L': actions.go_to_library,
            'R': partial(actions.reset_display, 'start')
        }
    }
}


for i, item in enumerate(system_menu):
    action = system_menu[item]
    bindings['system_menu']['single'][str(i + 2)] = action


def check(driver, state):
    buttons = driver.get_buttons()
    location = state['app']['location']
    if type(location) == int:
        location = 'book'
    for _id in buttons:
        _type = buttons[_id]
        try:
            store.dispatch(bindings[location][_type][_id]())
        except KeyError:
            log.debug('no binding for key {}, {} press'.format(_id, _type))
