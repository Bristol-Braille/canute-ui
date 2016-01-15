#!/usr/bin/env python
import argparse
import pickle
import logging
import time
import os.path
from driver import Driver
from pageable import Menu, Book, Library
from utility import write_pid_file, remove_pid_file
import buttons_config
import config_loader


class UI():
    """This is the UI class which is a framework to build a UI for the braille
    machine

    This implements the spec in [README.md](README.md)

    The UI can be configured to either use the :class:`.Pi` or
    :class:`.Emulated` driver class.

    :param driver: the :class:`driver` object that abstracts the hardware
    """

    state_file = 'ui.pkl'

    def __init__(self, driver, config):
        self.driver = driver
        self.dimensions = self.driver.get_dimensions()
        self.last_data = []

        # load the books into the library
        self.library = Library(self.dimensions, config, self)
        self.menu = Menu(self.dimensions, config, self)

        # the screen is the object that is shown and operated on by the buttons, it will be either the library or the book
        self.load_state()
        if self.state['mode'] == 'book':
            log.info("starting in book mode")
            self.book = self.library.get_book(self.state['book_num'])
            self.screen = self.book
            self.show()
        elif self.state['mode'] == 'library':
            log.info("starting in library mode")
            self.screen = self.library
            self.show()
        elif self.state['mode'] == 'menu':
            log.info("starting in menu mode")
            self.screen = self.menu
            self.show()



    def save_state(self):
        with open(UI.state_file, 'w') as fh:
            pickle.dump(self.state, fh)

    def load_state(self):
        try:
            with open(UI.state_file) as fh:
                self.state = pickle.load(fh)
        except IOError:
            log.debug("no state file; initialising")
            self.state = {}
            self.state['mode'] = 'library'
            self.state['book_num'] = 0

    def despatch(self,button_type, button_num):
        # we're using a hash to store config, so convert number to a str
        button_num = str(button_num)
        # fetch the config for the button
        try:
            config = buttons_config.conf[self.state['mode']][button_type][button_num]
        except KeyError:
            # try get the default
            try:
                config = buttons_config.conf['default'][button_type][button_num]
            except KeyError:
                # otherwise return False
                log.debug("nothing defined for that button")
                return False

        # to call the method we need the object
        if config['obj'] == 'ui':
            obj = self
        elif config['obj'] == 'screen':
            obj = self.screen

        # get the method
        try:
            method = getattr(obj, config['method'])
        except AttributeError:
            log.warning("object %s has no method %s to call" % (obj, config['method']))
            return False

        # we're going to do something, so make an OK sound
        self.driver.send_ok_sound()

        # call method, maybe with args
        if config.has_key('args'):
            log.info("despatching %s->%s(%s)" % (config['obj'], config['method'], config['args']))
            method(config['args'])
        else:
            log.info("despatching %s->%s()" % (config['obj'], config['method']))
            method()

        # update the screen
        self.show()
        return True

    def start(self):
        '''start the UI running, runs the UI until the driver returns an error'''
        while self.driver.is_ok():
            # fetch all buttons (a fetch resets button register)
            buttons = self.driver.get_buttons()
            for button_num in range(8):
                if buttons[button_num] != False:
                    button_type = buttons[button_num]
                    # if a button is pressed, deal with it
                    result = self.despatch(button_type, button_num)
                    if result is False:
                        self.driver.send_error_sound()
            time.sleep(0.1)
        else:
            log.info("UI main loop ending")

    def library_mode(self):
        log.info("library mode")
        self.state['mode'] = 'library'
        self.screen = self.library
        self.library.check_for_new_books()

    def menu_mode(self):
        log.info("menu mode")
        self.state['mode'] = 'menu'
        self.screen = self.menu

    def load_book(self, number):
        '''
        load a book into self.book, set the screen to point at the book
        update the screen. If no book, don't set and update the screen
        '''
        try:
            self.book = self.library.get_book(number)
            self.screen = self.book
            self.state['book_num'] = number
            self.state['mode'] = 'book'
        except IndexError as e:
            log.warning("no book at slot %d" % number)
            self.driver.send_error_sound()

    def show(self):
        '''shows the current screen object's braille, but only if it's changed from last time'''
        data = self.screen.show()

        if data == self.last_data:
            log.info("not updating display with identical data")
            self.driver.send_error_sound()
            return

        self.driver.set_braille(data)
        self.last_data = data
        self.save_state()
        log.info("display updated")

def setup_logs():
    log_file = config.get('files', 'log_file')
    log_format = logging.Formatter('%(asctime)s - %(name)-16s - %(levelname)-8s - %(message)s')
    # configure the client logging
    log = logging.getLogger('')
    # has to be set to debug as is the root logger
    log.setLevel(logging.DEBUG)

    # create console handler and set level to info
    ch = logging.StreamHandler()
    ch.setLevel(args.loglevel)

    # create formatter for console
    ch.setFormatter(log_format)
    log.addHandler(ch)

    # create file handler and set to debug
    fh = logging.FileHandler(log_file)
    fh.setLevel(args.loglevel)

    fh.setFormatter(log_format)
    log.addHandler(fh)

    return log

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Canute UI")

    parser.add_argument('--pi-buttons', action='store_const', dest='pi_buttons', const=True, default=False, help="use the Pi to handle button presses")
    parser.add_argument('--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO, help="debugging content")
    parser.add_argument('--text', action='store_const', dest='text', const=True, help="show text instead of braille")
    parser.add_argument('--tty', action='store', dest='tty', help="serial port for Canute stepstix board", default='/dev/ttyACM0')
    parser.add_argument('--delay', action='store', dest='delay', help="simulate mechanical delay in milliseconds", default=0, type=int)
    parser.add_argument('--disable-emulator', action='store_const', dest='emulated', const=False, default=True, help="do not show the graphical emulator")
    parser.add_argument('--both', action='store_const', dest='both', const=True, default=False, help="run both the emulator and the real hardware at the same time")

    args = parser.parse_args()

    config = config_loader.load()
    config.read('config.rc')
    library_dir = config.get('files', 'library_dir')
    config.set('files', 'library_dir', os.path.expanduser(library_dir))

    log = setup_logs()

    if not buttons_config.test_config():
        log.exception("bad button config")
        exit(1)

    # write pid file
    write_pid_file()

    try:
        if args.emulated and not args.both:
            log.info("running with emulated hardware")
            from driver_emulated import Emulated
            with Emulated(delay=args.delay, display_text=args.text) as driver:
                ui = UI(driver, config)
                ui.start()
        elif args.emulated and args.both:
            log.info("running with both emulated and real hardware on port %s" % args.tty)
            from driver_both import DriverBoth
            with DriverBoth(port=args.tty, pi_buttons=args.pi_buttons, delay=args.delay, display_text=args.text) as driver:
                ui = UI(driver, config)
                ui.start()
        else:
            log.info("running with real hardware on port %s" % args.tty)
            from driver_pi import Pi
            with Pi(port=args.tty, pi_buttons=args.pi_buttons) as driver:
                ui = UI(driver, config)
                ui.start()
    except Exception as e:
        log.exception(e)
    finally:
        remove_pid_file()
