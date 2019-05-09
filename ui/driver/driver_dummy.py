import sys
import logging
import random
import time
from collections import namedtuple

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
    button_map = (
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
    )
    button_choice = list()
    FuzzPress = namedtuple('FuzzPress', field_names=['button', 'up_at'])

    # FIXME: copied, with margin, from buttons.py which has no constant
    LONG_PRESS_DURATION = 0.55  # seconds

    def __init__(self, fuzz=True, seed=None):
        super(Dummy, self).__init__()
        self.fuzz = fuzz
        self.fuzz_press = None
        if not seed:
            seed = random.randint(0, 1000000)
            log.info('fuzz seed is %d' % seed)
        random.seed(seed)

    def is_ok(self):
        return True

    def _get_random_button(self):
        ''' get buttons in random order but always go through entire list
        before repeating any buttons'''
        if len(self.button_choice) == 0:
            self.button_choice = list(self.button_map)
            random.shuffle(self.button_choice)

        return self.button_choice.pop()

    def _get_random_press(self):
        '''Create a random button press event.

        Fixed odds of getting a long press, 1 in 20.
        '''
        _long = random.random() > 0.95
        if _long:
            up_at = time.time() + self.LONG_PRESS_DURATION
        else:
            # Short presses can end at the next call; no minimum time
            up_at = time.time()
        return self.FuzzPress(button=self._get_random_button(), up_at=up_at)

    def get_buttons(self):
        '''get button states

        In fuzz mode this presses only one button at a time.
        :rtype: dict of elements either set to 'down' or 'up'
        '''
        if not self.fuzz:
            # No presses ever get simulated without fuzz.
            return dict()

        report = {}

        if self.fuzz_press and time.time() >= self.fuzz_press.up_at:
            report[self.fuzz_press.button] = 'up'
            self.fuzz_press = None

        if not self.fuzz_press:
            self.fuzz_press = self._get_random_press()
            report[self.fuzz_press.button] = 'down'

        return report

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

    async def async_get_data(self, expected_cmd):
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
