import logging
import signal
from datetime import datetime
from .state import state
from .config_loader import import_pages

log = logging.getLogger(__name__)

page_buttons = import_pages('buttons')

bindings = { p:m.buttons for p, m in page_buttons.items() }
bindings['help_menu'] = {
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
}

# add a signal handler to manage going to the system menu when the rear
# button is pressed (generates a usr1 signal)
def sigusr1_helper(*args):
    state.app.go_to_system_menu()
signal.signal(signal.SIGUSR1, sigusr1_helper)

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
