import os
from functools import partial
import time

import logging
log = logging.getLogger(__name__)

import utility
import argparser
import buttons_config
import config_loader
from ui import setup_logs
from store import store
from actions import actions

def main():
    args = argparser.parser.parse_args()

    config = config_loader.load()
    library_dir = config.get('files', 'library_dir')
    log = setup_logs(config, args.loglevel)

    from driver_emulated import Emulated
    with Emulated(delay=args.delay, display_text=args.text) as driver:
        quit = False
        store.subscribe(partial(handle_changes, driver, config))
        file_names = utility.find_files(library_dir, ('canute',))
        store.dispatch(actions.set_books(file_names))
        while not quit:
            buttons = driver.get_buttons()
            state = store.get_state()
            bindings = state['button_bindings']
            location = state['location']
            if type(location) == int:
                location = 'book'
            for _id in buttons:
                _type = buttons[_id]
                store.dispatch(bindings[location][_type][_id]())




def handle_changes(driver, config):
    state = store.get_state()
    render(driver, state)
    if state['replace_library'] == 'start':
        log.debug(config)


previous_data = []
def set_display(driver, data, page, height):
    global previous_data
    n = page * height
    data = data[n: n + height]
    data = utility.flatten(data)
    if data != previous_data:
        driver.set_braille(data)
        previous_data = data
    else:
        log.debug('not setting display with identical data')


def render(driver, state):
    width = state['display']['width']
    height = state['display']['height']
    location = state['location']
    if location == 'library':
        page = state['library']['page']
        data = state['library']['data']
        set_display(driver, data, page, height)
    elif location == 'menu':
        page = state['menu']['page']
        data = state['menu']['data']
        set_display(driver, data, page, height)
    elif type(location) == int:
        page = state['books'][location]['page']
        data = state['books'][location]['data']
        set_display(driver, data, page, height)


if __name__ == '__main__':
    main()
