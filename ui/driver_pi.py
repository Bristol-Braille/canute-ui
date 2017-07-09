from .driver import Driver
from . import comms_codes as comms
import time
import serial
import logging
import struct
import binascii
import queue
import threading
import serial.tools.list_ports

log = logging.getLogger(__name__)

long_press = 500.0  # ms
double_click = 200.0  # ms
debounce = 20  # ms

try:
    import evdev
except ImportError:
    log.warning('Could not import evdev')


class Pi(Driver):
    '''driver class for use with the Raspberry Pi

    connects to the display via serial and knows how to send and receive data
    to it

    :param port: the serial port the display is plugged into
    :param pi_buttons: whether to use the evdev input for button presses
    '''

    def __init__(self, port=None, pi_buttons=False, timeout=60):
        self.timeout = timeout
        # get serial connection
        if port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p[2] == 'USB VID:PID=2341:8036 SNR=HIDPC':
                    port = p[0]
                    log.info('autoselecting serial port {}'.format(port))
                    break
        if port:
            self.port = self.setup_serial(port)
            log.info('hardware detected on port %s' % port)
        else:
            self.port = None

        super(Pi, self).__init__()

        if pi_buttons:
            self.button_queue = queue.Queue()
            self.button_thread = threading.Thread(target=self.button_loop)
            self.button_thread.daemon = True
            self.button_thread.start()

    def button_loop(self):
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        device = None
        for d in devices:
            if d.name == 'Bristol Braille Canute Buttons':
                device = d
                break
        if device is None:
            log.error('Arduino not found')
            return
        for event in device.read_loop():
            self.button_queue.put(event)

    def setup_serial(self, port):
        '''sets up the serial port with a timeout and flushes it.
        Timeout is set to 60s, as this is well beyond a full page refresh of
        the hardware

        :param port: the serial port the display is plugged into
        '''
        try:
            serial_port = serial.Serial()
            serial_port.port = port
            serial_port.timeout = float(self.timeout)
            serial_port.open()
            serial_port.flush()
            return serial_port
        except IOError as e:
            log.error('check usb connection to arduino %s', e)
            exit(1)

    def is_ok(self):
        '''checks the serial connection. There doesn't seem to be a specific
        method in pyserial so we're using getCD()'''
        try:
            self.port.getCD()
            return True
        # no port
        except AttributeError:
            return False
        # problem with the port
        except IOError:
            return False

    def get_buttons(self):
        '''get button states

        :rtype: list of elements either set to False (unpressed) or one of
        single, double, long
        '''
        buttons = {}
        if hasattr(self, 'button_queue'):
            for _ in range(100):
                try:
                    event = self.button_queue.get(timeout=0.001)
                    key = event.type == evdev.ecodes.EV_KEY
                    down = event.value == evdev.KeyEvent.key_down
                except queue.Empty:
                    event = None
                if event is not None and key and down:
                    e = evdev.ecodes
                    if (event.code == e.KEY_1):
                        buttons['1'] = 'single'
                    elif (event.code == e.KEY_2):
                        buttons['2'] = 'single'
                    elif (event.code == e.KEY_3):
                        buttons['3'] = 'single'
                    elif (event.code == e.KEY_4):
                        buttons['4'] = 'single'
                    elif (event.code == e.KEY_5):
                        buttons['5'] = 'single'
                    elif (event.code == e.KEY_6):
                        buttons['6'] = 'single'
                    elif (event.code == e.KEY_7):
                        buttons['7'] = 'single'
                    elif (event.code == e.KEY_8):
                        buttons['8'] = 'single'
                    elif (event.code == e.KEY_9):
                        buttons['9'] = 'single'
                    elif (event.code == e.KEY_LEFT):
                        buttons['<'] = 'single'
                    elif (event.code == e.KEY_RIGHT):
                        buttons['>'] = 'single'
                    elif (event.code == e.KEY_DOWN):
                        buttons['L'] = 'single'
                    elif (event.code == e.KEY_R):
                        buttons['R'] = 'single'
        return buttons

    def send_error_sound(self):
        '''make the hardware make an error sound'''
        log.debug('error sound')
        self.send_data(comms.CMD_SEND_ERROR)

    def send_ok_sound(self):
        '''make the hardware make an ok sound'''
        log.debug('ok sound')
        self.send_data(comms.CMD_SEND_OK)

    def send_data(self, cmd, data=[]):
        '''send data to the hardware

        :param cmd: command byte
        :param data: list of bytes
        '''
        message = struct.pack('%sb' % (len(data) + 1), cmd, *data)
        log.debug('tx cmd [%s]' % binascii.hexlify(message))
        self.port.write(message)

    def get_data(self, expected_cmd):
        '''gets 2 bytes of data from the hardware

        :param expected_cmd: what command we're expecting (error raised
        otherwise)

        :rtype: an integer return value
        '''
        log.debug('trying to read 2 bytes')
        message = self.port.read(2)
        log.debug('rx [%s]' % binascii.hexlify(message))
        if len(message) != 2:
            log.warning('unexpected rx data length %d' % len(message))
        data = struct.unpack('2b', message)
        if data[0] != expected_cmd:
            log.warning('unexpected rx command %d, expecting %d' %
                        (data[0], expected_cmd))
        return data[1]

    def __exit__(self, ex_type, ex_value, traceback):
        '''__exit__ method allows us to shut down the port properly'''
        if ex_type is not None:
            log.error('%s : %s' % (ex_type.__name__, ex_value))
        if self.port:
            log.error('closing serial port')
            self.port.close()
        if hasattr(self, 'button_thread'):
            self.button_thread.join()

    def __enter__(self):
        '''method required for using the `with` statement'''
        return self


Driver.register(Pi)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    pi = Pi(pi_buttons=True)
    while 1:
        buttons = pi.get_buttons()
        log.info('buttons: %s' % buttons)
        time.sleep(1)
