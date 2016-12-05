import os
from functools import partial
import time
import shutil
import pwd
import grp
import re

import logging
log = logging.getLogger(__name__)

import utility
import argparser
import buttons_config
import config_loader
from setup_logs import setup_logs
from store import store
from actions import actions
import convert

NATIVE_EXTENSION = 'canute'
BOOK_EXTENSIONS = (NATIVE_EXTENSION, 'pef', 'brf')

def main():
    args = argparser.parser.parse_args()

    config = config_loader.load()
    log = setup_logs(config, args.loglevel)
    library_dir = config.get('files', 'library_dir')

    from driver_emulated import Emulated
    with Emulated(delay=args.delay, display_text=args.text) as driver:
        quit = False
        store.subscribe(partial(handle_changes, driver, config))
        setup_library(library_dir)
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


def setup_library(library_dir):
    file_names = utility.find_files(library_dir, (NATIVE_EXTENSION,))
    store.dispatch(actions.set_books(file_names))

def refresh_library(library_dir):
    file_names = utility.find_files(library_dir, (NATIVE_EXTENSION,))
    store.dispatch(actions.check_books(file_names))


def convert_library(width, height, library_dir):
    file_names = utility.find_files(library_dir, BOOK_EXTENSIONS)
    for name in file_names:
        basename, ext = os.path.splitext(os.path.basename(name))
        if re.match('\.pef$', ext, re.I):
            log.info("converting pef to canute")
            native_file = library_dir + basename + '.' + NATIVE_EXTENSION
            convert.convert_pef(width, height, name, native_file)
        elif re.match('\.brf$', ext, re.I):
            log.info("converting brf to canute")
            native_file = library_dir + basename + '.' + NATIVE_EXTENSION
            convert.convert_brf(width, height, name, native_file)



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
            log.debug('changing ownership of {} from {} to {}'.format(new_path, uid, gid))
            os.chown(new_path, uid, gid)
        store.dispatch(actions.replace_library(False))
        width = state['display']['width']
        height = state['display']['height']
        convert_library(width, height, library_dir)
        setup_library(library_dir)
        store.dispatch(actions.go_to_library())
    if state['backup_log']:
        usb_dir = config.get('files', 'usb_dir')
        log_file = config.get('files', 'log_file')
        # make a filename based on the date
        backup_file = os.path.join(usb_dir, time.strftime('%Y%m%d_log.txt'))
        log.warning('backing up log to USB stick: {}'.format(backup_file))
        try:
            shutil.copyfile(log_file, backup_file)
        except IOError as e:
            log.warning("couldn't backup log file: {}".format(e))
        store.dispatch(actions.backup_log(False))


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
