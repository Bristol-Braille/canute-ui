from .driver import Driver
import time
import logging
import sys
from multiprocessing import Process, Queue
from queue import Empty
from . import comms_codes as comms
from . import qt_display

log = logging.getLogger(__name__)


class Emulated(Driver):

    # hardware defs
    CHARS = 40
    ROWS = 9

    '''driver class that emulates the machine with a GUI

    we fake the :func:`send_data` and :func:`get_data` functions

    The :class:`Display` class is used to show how the braille machine would
    look and provide buttons.

    message passing is done with queues
    '''

    prev_data = [(0,) * 40] * 9

    def __init__(self, delay=0, display_text=False):
        super(Emulated, self).__init__()
        self.data = 0
        self.delay = delay
        self.buttons = {}

        # message passing queues: pass messages to display on parent, fetch
        # messages on chlid
        self.send_queue = Queue()
        self.receive_queue = Queue()
        # start the gui program as a separated process
        self.process = Process(target=qt_display.start,
                               kwargs={
                                   'to_display_queue': self.send_queue,
                                   'from_display_queue': self.receive_queue,
                                   'display_text': display_text
                               })
        self.process.daemon = True
        self.process.start()
        log.info('started qt_display.py with process id %d' % self.process.pid)

    def is_ok(self):
        '''The UI needs to know when to quit, so the GUI can tell it using this
        method'''
        return self.process.is_alive()

    def send_error_sound(self):
        log.info('error sound!')

    def send_ok_sound(self):
        log.info('ok sound!')

    def __exit__(self, ex_type, ex_value, traceback):
        '''__exit__ method allows us to shut down the threads properly'''
        if ex_type is not None:
            log.error('%s : %s' % (ex_type.__name__, ex_value))
        if self.process.is_alive() is None:
            log.info('killing GUI subprocess')
            self.process.terminate()
        log.info('done')

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self

    def get_buttons(self):
        '''Return the current button state and reset to all unpressed

        :rtype: list of 8 elements either set to False (unpressed) or one of
        single, double, long
        '''
        try:
            msg = self.receive_queue.get(timeout=0.01)
            log.debug('got button msg %s' % msg)
            self.buttons[msg['id']] = msg['type']
        except Empty:
            pass

        ret = self.buttons
        # reset
        self.buttons = {}
        return ret

    def send_data(self, cmd, data=[]):
        '''send data to the hardware. We fake the return data by making a note
        of the command the only thing we really do is if the command is to send
        data. Then we pass on to the display emulator

        :param cmd: command byte
        :param data: list of bytes
        '''
        if cmd == comms.CMD_GET_CHARS:
            self.data = Emulated.CHARS
        elif cmd == comms.CMD_GET_ROWS:
            self.data = Emulated.ROWS
        elif cmd == comms.CMD_SEND_PAGE:
            log.error('CMD_SEND_PAGE is no longer supported')
            sys.exit(1)
        elif cmd == comms.CMD_SEND_ERROR:
            log.error('making error sound!')
        elif cmd == comms.CMD_SEND_OK:
            log.error('making OK sound!')
        elif cmd == comms.CMD_SEND_LINE:
            self.data = 0
            if self.prev_data[data[0]] != tuple(data[1:]):
                time.sleep(self.delay / 1000.0)
            self.send_queue.put_nowait([comms.CMD_SEND_LINE] + data)
            self.prev_data[data[0]] = tuple(data[1:])
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


Driver.register(Emulated)
