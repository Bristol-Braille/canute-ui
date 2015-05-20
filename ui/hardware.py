import string
import time
import serial
import logging
import struct
import binascii
log = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    from threading import Timer
    from status_led import LedThread
    long_press = 1000.0 #ms
    double_click = 500.0 #ms
    debounce = 100 #ms
except ImportError:
    pass


class HardwareError(Exception):
    pass


class Hardware():
    """class that represents the hardware

    connects to the display via serial and knows how to send and receive data to it

    :param port: the serial port the display is plugged into
    :param using_pi: whether to use the Pi for button presses
    """
    def __init__(self, port='/dev/ttyACM0', using_pi=False):
        # get serial connection
        if port:
            self.port = self.setup_serial(port)
            log.info("hardware detected on port %s" % port)
        else:
            self.port = None

        self.using_pi = using_pi
        self.buttons = [False] * 8
        if using_pi:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            self.led_thread=LedThread(21,0.5)
            self.led_thread.start()
            self.pi_buts = [16, 19, 15, 18, 26, 22, 23, 24]
            # need to store some details to work out what kind of click it was 
            self.pi_but_time_press = [0] * 8
            self.pi_but_time_release = [0] * 8
            self.pi_but_clicks = [0] * 8
            for pin in self.pi_buts:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.button_int, bouncetime=debounce)
            log.info("setup buttons for pi")

    def determine_button_type(self, index):
        '''determines button type by how many clicks and timings
        '''
        if self.pi_but_clicks[index] == 2:
            self.buttons[index] = 'double'
        elif self.pi_but_clicks[index] == 1:
            # differentiate between long and single
            log.debug(self.pi_but_time_release[index] - self.pi_but_time_press[index])
            if self.pi_but_time_release[index] - self.pi_but_time_press[index] > (long_press / 1000):
                self.buttons[index] = 'long'
            else:
                self.buttons[index] = 'single'

        # reset button presses
        self.pi_but_clicks[index] = 0

    def button_int(self, channel):
        '''interrupt routine for all the buttons.
        makes a note of how many times a button's been pressed, and when it was pressed and released
        sets a timer for 0.5 seconds from when button was pressed to call a determine_button_type that then decides what type
        of button click it was.
        '''
        state = GPIO.input(channel)
        log.debug("button %d is %s" % (channel, state))
        index = self.pi_buts.index(channel)

        # make a note of num clicks, press and release times
        if state == 0:  # pressed
            self.pi_but_time_press[index] = time.time()
            self.pi_but_clicks[index] += 1
        else:  # released
            # set a timer to decide what type of button it was
            t = Timer(double_click/1000, self.determine_button_type, [index])
            t.start()
            self.pi_but_time_release[index] = time.time()

    def setup_serial(self, port):
        '''sets up the serial port with a timeout and flushes it.
        Timeout is set to 60s, as this is well beyond a full page refresh of the hardware

        :param port: the serial port the display is plugged into
        '''
        try:
            serial_port = serial.Serial()
            serial_port.port = port
            serial_port.timeout = 60.0
            serial_port.open()
            serial_port.flush()
            return serial_port
        except IOError as e:
            log.error("check usb connection to arduino %s", e)
            exit(1)

    def is_ok(self):
        '''checks the serial connection. There doesn't seem to be a specific method in pyserial so we're using getCD()'''
        try:
            self.port.getCD()
            return True
        except IOError:
            return False

    def get_buttons(self):
        '''get button states - will be done by the Pi for now but will be done on the micro later

        :rtype: list of 8 elements either set to False (unpressed) or one of single, double, long
        '''
        if self.using_pi is True:
            buttons = self.buttons
            self.buttons = [False] * 8
            return buttons
        else:
            return [False] * 8

    def send_data(self, cmd, data=[]):
        '''send data to the hardware

        :param cmd: command byte
        :param data: list of bytes
        '''
        message = struct.pack('%sb' % (len(data) + 1), cmd, *data)
        log.debug("tx [%s]" % binascii.hexlify(message))
        self.port.write(message)

    def get_data(self, expected_cmd):
        '''gets 2 bytes of data from the hardware

        :param expected_cmd: what command we're expecting (error raised otherwise)
        :rtype: an integer return value
        '''
        message = self.port.read(2)
        log.debug("rx [%s]" % binascii.hexlify(message))
        if len(message) != 2:
            raise HardwareError("unexpected rx data length %d" % len(message))
        data = struct.unpack('2b', message)
        if data[0] != expected_cmd:
            raise HardwareError("unexpected rx command %d" % expected_cmd)
        return data[1]

    def __exit__(self, ex_type, ex_value, traceback):
        '''__exit__ method allows us to shut down the port properly'''
        if ex_type is not None:
            log.error("%s : %s" % (ex_type.__name__, ex_value))
        if self.port:
            log.error("closing serial port")
            self.port.close()
        if self.using_pi:
            self.led_thread.stop()
            self.led_thread.join()
            GPIO.cleanup()

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

    with Hardware(port=None, using_pi=True) as hardware:
        while True:
            log.info(hardware.get_buttons())
            time.sleep(1)
