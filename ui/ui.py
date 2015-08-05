#!/usr/bin/env python
import ipdb
import argparse
import pickle
import os
import logging
import time
import random
from driver import Driver
from pageable import Menu, Book, Library
from utility import test_book, write_pid_file, remove_pid_file
from ConfigParser import ConfigParser, NoSectionError, NoOptionError


class UI():
    """This is the UI class which is a framework to build a UI for the braille machine

    This implements the spec in [README.md](README.md)

    The UI can be configured to either use the :class:`.Hardware` or :class:`.HardwareEmulator` class.

    :param driver: the :class:`driver` object that abstracts the hardware
    """

    state_file = 'ui.pkl'

    def __init__(self, driver, config, button_config):
        self.driver = driver
        self.dimensions = self.driver.get_dimensions()
        self.last_data = []
        self.button_config = button_config

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

    def despatch(self,buttons):
        for button_num in range(8):
            if buttons[button_num] != False:
                button_type = buttons[button_num]
                mtype = self.screen.__class__.__name__.lower()
                config = self.button_config[mtype][button_num][button_type]
                if not config.has_key('object'):
                    config = self.button_config['default'][button_num][button_type]
                if not config.has_key('object'):
                    log.debug("nothing defined for that button")
                    return False

                log.debug(config)
                if config['object'] == 'ui':
                    obj = self
                elif config['object'] == 'screen':
                    obj = self.screen
                else:
                    log.warning("no config for object type %s" % config['object'])
                    return False
                #get the method
                try:
                    method = getattr(obj, config['method'])
                except AttributeError:
                    log.warning("object %s has no method %s to call" % (obj, config['method']))
                    return False
                    
                #call it
                log.debug("calling %s->%s(%s)" % (config['object'], config['method'], config['args']))

                #we're going to do something, so make an OK sound
                self.driver.send_ok_sound()
                if config['args'] is None:
                    method()
                else:
                    method(config['args'])
                #update the screen
                self.show()
                return True

    def start(self):
        '''start the UI running, runs the UI until the driver returns an error'''
        while self.driver.is_ok():
            # fetch all buttons (a fetch resets button register)
            buts = self.driver.get_button_status()
            result = self.despatch(buts)
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
    log_format = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
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

    parser.add_argument('--using-pi', action='store_const', dest='using_pi', const=True, default=False, help="use the Pi to handle button presses")
    parser.add_argument('--debug', action='store_const', dest='loglevel', const=logging.DEBUG, default=logging.INFO, help="debugging content")
    parser.add_argument('--tty', action='store', dest='tty', help="serial port for Canute stepstix board", default='/dev/ttyACM0')
    parser.add_argument('--delay', action='store', dest='delay', help="simulate mechanical delay in milliseconds", default=8000, type=int)
    parser.add_argument('--emulated', action='store_const', dest='emulated', const=True, default=False, help="emulate the hardware (use GUI)")

    args = parser.parse_args()

    # config
    config = ConfigParser()
    config.read('config.rc')
    log = setup_logs()

    #setup buttons

    from collections import defaultdict
    l=lambda:defaultdict(l)
    button_config=l()
    for mtype in ['default','library','book','menu']:
        for b in range(8):
            
            for btype in ['long','single','double']:
                try:
                    conf = config.get('button-%s' % mtype, 'b%s_%s' % (b,btype))
                    try:
                        obj,method,m_args = conf.split(',')
                        m_args = int(m_args)
                    except ValueError:
                        obj,method = conf.split(',')
                        m_args = None
                    button_config[mtype][b][btype] = { 'method' : method, 'args' : m_args, 'object' : obj }
                    log.debug("%s->%s->%s = %s->%s(%s)" % (mtype, b, btype, obj,method, m_args)) 
                except NoOptionError:
                    pass


    # write pid file
    write_pid_file()

    try:
        if args.emulated:
            log.info("running with emulated hardware")

            from hardware_emulator import HardwareEmulator
            with HardwareEmulator(delay=args.delay) as hardware:
                driver = Driver(hardware)
                ui = UI(driver, config, button_config)
                ui.start()
        else:
            log.info("running with stepstix hardware on port %s" % args.tty)
            from hardware import Hardware
            with Hardware(port=args.tty, using_pi=args.using_pi) as hardware:
                driver = Driver(hardware)
                ui = UI(driver, config, button_config)
                ui.start()
    except Exception as e:
        log.exception(e)
    finally:
        remove_pid_file()
