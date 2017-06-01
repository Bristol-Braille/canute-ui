import os
from frozendict import frozendict
from functools import partial
import time
import shutil
import logging

from ui.driver_pi import Pi
import ui.utility as utility
import ui.argparser as argparser
import ui.config_loader as config_loader
from ui.setup_logs import setup_logs
from ui.store import store
from ui.actions import actions, get_max_pages, dimensions
import ui.initial_state as initial_state
from ui.button_bindings import button_bindings
import ui.library as library


log = logging.getLogger(__name__)


def main():
    args = argparser.parser.parse_args()
    config = config_loader.load()
    log = setup_logs(config, args.loglevel)

    if args.emulated and not args.both:
        log.info("running with emulated hardware")
        from ui.driver_emulated import Emulated
        with Emulated(delay=args.delay, display_text=args.text) as driver:
            run(driver, config)
    elif args.emulated and args.both:
        log.info(
            "running with both emulated and real hardware on port %s"
            % args.tty
        )
        from ui.driver_both import DriverBoth
        with DriverBoth(port=args.tty, pi_buttons=args.pi_buttons,
                        delay=args.delay, display_text=args.text) as driver:
            run(driver, config)
    else:
        timeout = config.get('comms', 'timeout')
        log.info("running with real hardware on port %s, timeout %s" %
                 (args.tty, timeout))
        with Pi(port=args.tty,
                pi_buttons=args.pi_buttons,
                timeout=timeout) as driver:
            run(driver, config)


def run(driver, config):
    state = initial_state.read()
    width, height = driver.get_dimensions()
    state = state.copy(app=state['app'].copy(
        display=frozendict({'width': width, 'height': height})))
    state = state.copy(hardware=state['hardware'].copy(
        resetting_display='start'))
    store.dispatch({'type': 'init', 'value': state})
    library.sync(state, config.get('files', 'library_dir'))
    store.subscribe(partial(handle_changes, driver, config))

    # if we startup and update_ui is still 'in progress' then we are using the
    # old state file
    # and update has failed
    if state['app']['update_ui'] == 'in progress':
        store.dispatch(actions.update_ui('failed'))

    # since handle_changes subscription happens after init and library.sync it
    # may not have triggered. so we trigger it here. if we put it before init
    # it will start of by rendering a possibly invalid state. library.sync
    # won't dispatch if the library is already in sync so there would be no
    # guarantee of the subscription triggering if subscribed before that.
    store.dispatch(actions.trigger())
    button_loop(driver)


def button_loop(driver):
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


def handle_changes(driver, config):
    state = store.get_state()
    render(driver, state)
    change_files(config, state)
    initial_state.write(state)
    if state['app']['shutting_down'] and isinstance(driver, Pi):
        os.system("sudo shutdown -h now")


def change_files(config, state):
    if state['app']['replacing_library'] == 'start':
        store.dispatch(actions.replace_library('in progress'))
        library.replace(config, state)
    if state['app']['backing_up_log'] == 'start':
        store.dispatch(actions.backup_log('in progress'))
        backup_log(config)
    if state['app']['update_ui'] == 'start':
        log.info("update ui = start")
        if utility.find_ui_update(config):
            store.dispatch(actions.update_ui('in progress'))
        else:
            log.info("update not found")
            store.dispatch(actions.update_ui('failed'))


def render(driver, state):
    width, height = dimensions(state['app'])
    location = state['app']['location']
    warming_up = state['hardware']['warming_up'] == 'in progress'
    resetting_display = state['hardware']['resetting_display'] == 'in progress'
    if state['hardware']['resetting_display'] == 'start':
        store.dispatch(actions.reset_display('in progress'))
        driver.reset_display()
        store.dispatch(actions.reset_display('done'))
    elif warming_up or resetting_display:
        # our render method can be called asynchronously, we don't don anything
        # unless these are done
        pass
    elif state['hardware']['warming_up'] == 'start':
        store.dispatch(actions.warm_up('in progress'))
        driver.warm_up()
        store.dispatch(actions.warm_up(False))
    elif state['app']['shutting_down']:
        if isinstance(driver, Pi):
            driver.clear_page()
    elif location == 'library':
        page = state['app']['library']['page']
        data = state['app']['library']['data']
        # subtract title from page height
        data_height = height - 1
        max_pages = get_max_pages(data, data_height)
        n = page * data_height
        data = data[n: n + data_height]
        # pad page with empty rows
        while len(data) < data_height:
            data += ((0,) * width,)
        title = format_title('library menu', width, page, max_pages)
        set_display(driver, tuple([title]) + tuple(data))
    elif location == 'menu':
        page = state['app']['menu']['page']
        data = state['app']['menu']['data']
        # subtract title from page height
        data_height = height - 1
        max_pages = get_max_pages(data, data_height)
        title = format_title('system menu', width, page, max_pages)
        n = page * data_height
        data = data[n: n + data_height]
        # pad page with empty rows
        while len(data) < data_height:
            data += ((0,) * width,)
        set_display(driver, tuple([title]) + tuple(data))
    elif type(location) == int:
        page = state['app']['books'][location]['page']
        data = state['app']['books'][location]['data']
        n = page * height
        data = data[n: n + height]
        set_display(driver, data)


previous_data = []


def set_display(driver, data):
    global previous_data
    if data != previous_data:
        for row, braille in enumerate(data):
            driver.set_braille_row(row, braille)
        previous_data = data
    else:
        log.debug('not setting page with identical data')


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


def format_title(title, width, page_number, total_pages):
    '''
    format a title like this:
        * title on the top line.
        * use two dot-six characters to indicate all uppercase for the title.
        * page numbers all the way at the right with 3 digits out of total,
        e.g. 001 / 003.
    '''
    # hack - leave space at the beginning for the uppercase symbols
    uppercase = '  '
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


if __name__ == '__main__':
    main()
