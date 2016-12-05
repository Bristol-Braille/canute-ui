import os
from functools import partial
import time
import shutil
import pwd
import grp

import logging
log = logging.getLogger(__name__)

import utility
import argparser
import buttons_config
import config_loader
from setup_logs import setup_logs
from store import store
from actions import actions

NATIVE_EXTENSION = 'canute'
BOOK_EXTENSIONS = (NATIVE_EXTENSION, 'pef', 'brf')

def main():
    args = argparser.parser.parse_args()

    config = config_loader.load()
    log = setup_logs(config, args.loglevel)

    from driver_emulated import Emulated
    with Emulated(delay=args.delay, display_text=args.text) as driver:
        quit = False
        store.subscribe(partial(handle_changes, driver, config))
        setup_library(config)
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
    change_files(config, state)


def setup_library(config):
    library_dir = config.get('files', 'library_dir')
    file_names = utility.find_files(library_dir, (NATIVE_EXTENSION,))
    store.dispatch(actions.set_books(file_names))



def change_files(config, state):
    if state['replace_library']:
        library_dir = config.get('files', 'library_dir')
        usb_dir = config.get('files', 'usb_dir')
        owner = config.get('user', 'user_name')
        wipe_library(library_dir)
        new_books = utility.find_files(usb_dir, BOOK_EXTENSIONS)
        uid = pwd.getpwnam(owner).pw_uid
        gid = grp.getgrnam(owner).gr_gid
        for filename in new_books:
            log.info('copying {} to {}'.format(filename, library_dir))
            shutil.copy(filename, library_dir)

            # change ownership
            basename = os.path.basename(filename)
            new_path = library_dir + basename
            log.debug('changing ownership of {} to {} to {}'.format(new_path, uid, gid))
            os.chown(new_path, uid, gid)
        store.dispatch(actions.replace_library(False))
        setup_library(config)
        store.dispatch(actions.go_to_library())



def wipe_library(library_dir):
    for book in utility.find_files(library_dir, BOOK_EXTENSIONS):
        os.remove(book)


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
