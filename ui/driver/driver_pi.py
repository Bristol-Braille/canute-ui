from .driver import Driver
from . import comms_codes as comms
import time
import serial
import logging
import struct
import serial.tools.list_ports

log = logging.getLogger(__name__)

long_press = 500.0  # ms
double_click = 200.0  # ms
debounce = 20  # ms


class Pi(Driver):
    '''driver class for use with the Raspberry Pi

    connects to the display via serial and knows how to send and receive data
    to it

    :param port: the serial port the display is plugged into
    '''

    def __init__(self, port=None, timeout=60):
        self.timeout = timeout
        # get serial connection
        if port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p[2].startswith('USB VID:PID=2341'):
                    port = p[0]
                    log.info('autoselecting serial port {}'.format(port))
                    break
        if port:
            self.port = self.setup_serial(port)
            log.info('hardware detected on port %s' % port)
        else:
            self.port = None

        self.previous_buttons = tuple()

        super(Pi, self).__init__()

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
            serial_port.baudrate = 9600
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

        :rtype: dict of elements either set to 'down' or 'up'
        '''
        mapping = {
            '0': 'R',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': 'X',
            '11': '<',
            '12': 'L',
            '13': '>',
        }
        buttons = {}
        self.send_data(comms.CMD_SEND_BUTTONS)
        read_buttons = self.get_data(comms.CMD_SEND_BUTTONS)
        down = list(self.previous_buttons)
        for i, n in enumerate(reversed(list('{:0>14b}'.format(read_buttons)))):
            name = mapping[str(i)]
            if n == '1' and (name not in self.previous_buttons):
                buttons[name] = 'down'
                down.append(name)
            elif n == '0' and (name in self.previous_buttons):
                buttons[name] = 'up'
                down.remove(name)

        self.previous_buttons = tuple(down)

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
        self.port.write(message)

    def get_data(self, expected_cmd):
        '''gets 2 bytes of data from the hardware

        :param expected_cmd: what command we're expecting (error raised
        otherwise)

        :rtype: an integer return value
        '''
        message = self.port.read(3)
        if len(message) < 2:
            log.warning('unexpected rx data length %d' % len(message))
        data = struct.unpack('3b', message)
        if data[0] != expected_cmd:
            log.warning('unexpected rx command %d, expecting %d' %
                        (data[0], expected_cmd))
        return data[1] | (data[2] << 8)

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
