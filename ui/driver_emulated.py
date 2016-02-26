from driver import Driver
import time
import logging
from udp_utility import udp_send, udp_recv
from comms_codes import *
import subprocess

log = logging.getLogger(__name__)



class Emulated(Driver):

    # hardware defs
    BUTTONS = 8
    CHARS = 28
    ROWS = 4

    """driver class that emulates the machine with a GUI

    we fake the :func:`send_data` and :func:`get_data` functions

    The :class:`Display` class is used to show how the braille machine would look and provide buttons.

    message passing is done with queues
    """

    def __init__(self, delay=0, display_text=False):
        super(Emulated, self).__init__()
        self.data = 0
        self.delay = delay
        self.buttons = [False] * Emulated.BUTTONS

        # message passing queues: pass messages to display on parent, fetch messages on chlid
        self.udp_send = udp_send(port=5000)
        self.udp_recv = udp_recv(port=5001)

        # start the gui program as a separated process as tkinter & threads don't play well
        process = ["./qt_display.py" ]
        if display_text:
            process.append("--text")
        self.process = subprocess.Popen(process)

        # wait for it to start up or it will miss the first communication
        time.sleep(0.5)
        log.info("started qt_display.py with process id %d" % self.process.pid)

    def is_ok(self):
        '''The UI needs to know when to quit, so the GUI can tell it using this method'''
        if self.process.poll() is None:
            return True
        else:
            return False

    def send_error_sound(self):
        log.info("error sound!");

    def send_ok_sound(self):
        log.info("ok sound!");

    def __exit__(self, ex_type, ex_value, traceback):
        '''__exit__ method allows us to shut down the threads properly'''
        if ex_type is not None:
            log.error("%s : %s" % (ex_type.__name__, ex_value))
        if self.process.poll() is None:
            log.info("killing GUI subprocess")
            self.process.kill()
        log.info("done")

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self

    def get_buttons(self):
        '''Return the current button state and reset to all unpressed

        :rtype: list of 8 elements either set to False (unpressed) or one of single, double, long
        '''
        msg = self.udp_recv.get()
        if msg is not None:
            log.debug("got button msg %s" % msg)
            self.buttons[msg['num']] = msg['type']
        ret = self.buttons
        # reset
        self.buttons = [False] * Emulated.BUTTONS
        return ret

    def send_data(self, cmd, data=[]):
        '''send data to the hardware. We fake the return data by making a note of the command
        the only thing we really do is if the command is to send data. Then we pass on to the display emulator

        :param cmd: command byte
        :param data: list of bytes
        '''
        if cmd == CMD_GET_CHARS:
            self.data = Emulated.CHARS
        elif cmd == CMD_GET_ROWS:
            self.data = Emulated.ROWS
        elif cmd == CMD_SEND_PAGE:
            self.data = 0
            log.debug("received data for emulator %s" % data)
            log.debug("delaying %s milliseconds to emulate hardware" % self.delay)
            time.sleep(self.delay / 1000.0)
            self.udp_send.put([CMD_SEND_PAGE] + data)
        elif cmd == CMD_SEND_ERROR:
            log.error("making error sound!")
        elif cmd == CMD_SEND_OK:
            log.error("making OK sound!")
        elif cmd == CMD_SEND_LINE:
            self.data = 0
            log.debug("received row data for emulator %s" % data)
            log.debug("delaying %s milliseconds to emulate hardware" % self.delay)
            time.sleep(self.delay / 1000.0)
            self.udp_send.put([CMD_SEND_LINE] + data)

    def get_data(self, expected_cmd):
        '''gets 2 bytes of data from the hardware - we're faking this so the driver doesn't complain

        :param expected_cmd: what command we're expecting (error raised otherwise)
        :rtype: an integer return value
        '''
        return self.data

Driver.register(Emulated)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)
    log.info("showing all braille pin pics")
    count = 0

    with Emulated() as driver:
        while driver.is_ok():
            log.info(driver.get_buttons())
            driver.send_data(CMD_SEND_PAGE, [count % 64]*Emulated.ROWS*Emulated.CHARS)
            count += 1
            time.sleep(1)
