import os
from functools import partial
import time
import shutil
import pwd
import grp
import re
from pydux.extend import extend
from driver_pi import Pi

import logging
log = logging.getLogger(__name__)

import utility
import argparser
import buttons_config
import config_loader
from setup_logs import setup_logs
from store import store
from actions import actions, get_max_pages, get_title
import convert
import initial_state
from button_bindings import button_bindings
from bookfile_list import BookFile_List


NATIVE_EXTENSION = 'canute'
BOOK_EXTENSIONS = (NATIVE_EXTENSION, 'pef', 'brf')

def main():
    args = argparser.parser.parse_args()

    config = config_loader.load()
    log = setup_logs(config, args.loglevel)

    if args.emulated and not args.both:
        log.info("running with emulated hardware")
        from driver_emulated import Emulated
        with Emulated(delay=args.delay, display_text=args.text) as driver:
            run(driver, config)
    elif args.emulated and args.both:
        log.info("running with both emulated and real hardware on port %s" % args.tty)
        from driver_both import DriverBoth
        with DriverBoth(port=args.tty, pi_buttons=args.pi_buttons,
                delay=args.delay, display_text=args.text) as driver:
            run(driver, config)
    else:
        # have to do this because couldn't find a way to set a default inside a section
        if config.has_option('comms', 'timeout'):
            timeout = float(config.get('comms', 'timeout'))
        else:
            timeout = 60
        log.info("running with real hardware on port %s, timeout %s" % (args.tty, timeout))
        with Pi(port=args.tty, pi_buttons=args.pi_buttons, timeout=timeout) as driver:
            run(driver, config)


def run(driver, config):
    quit = False
    init_state = initial_state.read()
    width, height = driver.get_dimensions()
    init_state['display'] = {'width': width, 'height': height}
    store.subscribe(partial(handle_changes, driver, config))
    store.dispatch(actions.init(init_state))
    while not quit:
        quit = button_loop(driver)


def button_loop(driver):
    buttons = driver.get_buttons()
    state = store.get_state()
    location = state['location']
    if not isinstance(driver, Pi):
        if not driver.is_ok():
            log.debug('shutting down due to GUI closed')
            store.dispatch(actions.shutdown(True))
        if state['shutting_down']:
            del driver
            return True
    if type(location) == int:
        location = 'book'
    for _id in buttons:
        _type = buttons[_id]
        try:
            store.dispatch(button_bindings[location][_type][_id]())
        except KeyError:
            log.debug('no binding for key {}, {} press'.format(_id, _type))
    return False


def handle_changes(driver, config):
    state = store.get_state()
    initial_state.write(state)
    render(driver, state)
    change_files(config, state)
    if state['shutting_down']:
        if isinstance(driver, Pi):
            os.system("sudo shutdown -h now")



def render(driver, state):
    width = state['display']['width']
    height = state['display']['height']
    location = state['location']
    if state['shutting_down']:
        driver.clear_page()
    elif location == 'library':
        page = state['library']['page']
        data = state['library']['data']
        height = height - 1
        max_pages = get_max_pages(data, height)
        n = page * height
        data = data[n : n + height]
        title = format_title('library menu', width, page, max_pages)
        set_display(driver, [title] + list(data))
    elif location == 'menu':
        page = state['menu']['page']
        data = state['menu']['data']
        height = height - 1
        max_pages = get_max_pages(data, height)
        title = format_title('system menu', width, page, max_pages)
        n = page * height
        data = data[n : n + height]
        set_display(driver, [title] + list(data))
    elif type(location) == int:
        page = state['books'][location]['page']
        data = state['books'][location]['data']
        n = page * height
        data = data[n : n + height]
        set_display(driver, data)


previous_data = []
def set_display(driver, data):
    global previous_data
    data = utility.flatten(data)
    if data != previous_data:
        driver.set_braille(data)
        previous_data = data
    else:
        log.debug('not setting display with identical data')


def setup_library(library_dir, width):
    file_names = utility.find_files(library_dir, (NATIVE_EXTENSION,))
    books = []
    for filename in file_names:
        books.append(
            {
                'data': BookFile_List(filename, width),
                'page': 0
            }
        )
    store.dispatch(actions.set_books(books))


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
    if state['replacing_library'] == 'start':
        store.dispatch(actions.replace_library('in progress'))
        replace_library(config, state)
    if state['backing_up_log'] == 'start':
        store.dispatch(actions.backup_log('in progress'))
        backup_log(config)


def format_title(title, width, page_number, total_pages):
    '''
    format a title like this:
        * title on the top line.
        * use two dot-six characters to indicate all uppercase for the title.
        * page numbers all the way at the right with 3 digits out of total, e.g. 001 / 003.
    '''
    uppercase = '  ' # hack - leave space at the beginning for the uppercase symbols
    title = "%s%s" % (uppercase, title)
    current_page = " %03d / %03d" % (page_number + 1, total_pages + 1)

    available_title_space = width - len(current_page)

    # make title right length
    if len(title) > available_title_space:
        # truncate
        title = title[0:available_title_space]
    else:
        # pad
        title += " " * (available_title_space - len(title))

    title_pins = utility.alphas_to_pin_nums(title + current_page)
    # replace first 2 chars with the uppercase symbols
    title_pins[0:2] = [32, 32]
    return title_pins


def replace_library(config, state):
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
    width = state['display']['width']
    height = state['display']['height']
    convert_library(width, height, library_dir)
    setup_library(library_dir, width)
    store.dispatch(actions.replace_library('done'))


def backup_log(config):
    usb_dir = config.get('files', 'usb_dir')
    log_file = config.get('files', 'log_file')
    # make a filename based on the date
    backup_file = os.path.join(usb_dir, time.strftime('%Y%m%d_log.txt'))
    log.warning('backing up log to USB stick: {}'.format(backup_file))
    try:
        shutil.copyfile(log_file, backup_file)
    except IOError as e:
        log.warning("couldn't backup log file: {}".format(e))
    store.dispatch(actions.backup_log('done'))


def wipe_library(library_dir):
    for book in utility.find_files(library_dir, BOOK_EXTENSIONS):
        os.remove(book)


if __name__ == '__main__':
    main()
