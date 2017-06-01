
import logging
from .store import store
from .driver_pi import Pi
from .button_bindings import button_bindings
from .actions import actions
from . import initial_state


log = logging.getLogger(__name__)


def run_loop(driver):
    quit = False
    while not quit:
        buttons = driver.get_buttons()
        state = store.get_state()
        location = state['app']['location']
        if not isinstance(driver, Pi):
            if not driver.is_ok():
                log.debug('shutting down due to GUI closed')
                store.dispatch(actions.shutdown())
            shutting_down = state['app']['shutting_down']
            update_ui = state['app']['update_ui'] == 'in progress'
            if shutting_down or update_ui:
                log.debug("shutting down due to state change")
                initial_state.write(state)
                quit = True
        if type(location) == int:
            location = 'book'
        for _id in buttons:
            _type = buttons[_id]
            try:
                store.dispatch(button_bindings[location][_type][_id]())
            except KeyError:
                log.debug('no binding for key {}, {} press'.format(_id, _type))
