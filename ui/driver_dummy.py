import sys
import logging
import random

from .driver import Driver
from . import comms_codes as comms

log = logging.getLogger(__name__)


class Dummy(Driver):
    '''driver class for testing without a GUI

    '''
    # hardware defs
    CHARS = 40
    ROWS = 9

    buttons = {}

    def __init__(self):
        super(Dummy, self).__init__()

    def is_ok(self):
        return True

    def get_buttons(self):
        '''get button states

        :rtype: dict of elements either set to 'down' or 'up'
        '''

        button_map = [
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '<',
            '>',
            'L',
            'R',
            'X',
        ]

        # raise any previously held keys
        for button in self.buttons.keys():
            if self.buttons[button] == 'down':
                self.buttons[button] = 'up'
            else:
                self.buttons[button]

        n = random.randint(0, len(button_map) - 1)
        self.buttons[button_map[n]] = 'down'

        return self.buttons

    def send_error_sound(self):
        '''make the hardware make an error sound'''
        log.debug('error sound')
        self.send_data(comms.CMD_SEND_ERROR)

    def send_ok_sound(self):
        '''make the hardware make an ok sound'''
        log.debug('ok sound')
        self.send_data(comms.CMD_SEND_OK)

    def send_data(self, cmd, data=[]):
        '''send data to the hardware. We fake the return data by making a note
        of the command the only thing we really do is if the command is to send
        data. Then we pass on to the display emulator

        :param cmd: command byte
        :param data: list of bytes
        '''
        if cmd == comms.CMD_GET_CHARS:
            self.data = self.CHARS
        elif cmd == comms.CMD_GET_ROWS:
            self.data = self.ROWS
        elif cmd == comms.CMD_SEND_PAGE:
            log.error('CMD_SEND_PAGE is no longer supported')
            sys.exit(1)
        elif cmd == comms.CMD_SEND_ERROR:
            log.error('making error sound!')
        elif cmd == comms.CMD_SEND_OK:
            log.error('making OK sound!')
        elif cmd == comms.CMD_SEND_LINE:
            self.data = 0
        elif cmd == comms.CMD_RESET:
            self.data = 0

    def get_data(self, expected_cmd):
        '''gets 2 bytes of data from the hardware - we're faking this so the
        driver doesn't complain

        :param expected_cmd: what command we're expecting (error raised
        otherwise)
        :rtype: an integer return value
        '''
        return self.data

    def __exit__(self, ex_type, ex_value, traceback):
        '''__exit__ method allows us to shut down the port properly'''
        if ex_type is not None:
            log.error('%s : %s' % (ex_type.__name__, ex_value))

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self


Driver.register(Dummy)
