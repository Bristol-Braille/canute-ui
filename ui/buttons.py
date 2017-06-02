import logging
from .store import store
from .button_bindings import button_bindings


log = logging.getLogger(__name__)


def check(driver, state):
    buttons = driver.get_buttons()
    location = state['app']['location']
    if type(location) == int:
        location = 'book'
    for _id in buttons:
        _type = buttons[_id]
        try:
            store.dispatch(button_bindings[location][_type][_id]())
        except KeyError:
            log.debug('no binding for key {}, {} press'.format(_id, _type))
