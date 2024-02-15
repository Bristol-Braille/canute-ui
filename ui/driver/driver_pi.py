import sys
import time
from .driver import Driver
import asyncio
from . import comms_codes as comms, simple_hdlc
import logging
import serial
import serial.tools.list_ports
import struct
import smbus2
import traceback

from .. import braille

log = logging.getLogger(__name__)

long_press = 500.0  # ms
double_click = 200.0  # ms

EEPROM_SIZE = 8 * 1024  # For M24C64 as in (at least) PCB v1.0, v1.1
EEPROM_PAGE_SIZE = 32
# -1 is serial number; -2 is flags.
DUTY_RECORD_PAGE = (EEPROM_SIZE // EEPROM_PAGE_SIZE) - 3
DUTY_RECORD_ADDR = DUTY_RECORD_PAGE * EEPROM_PAGE_SIZE
N_ROWS = 9
BYTES_PER_DUTY_RECORD = 3
ACTUATION_SAVE_PERIOD = 60 * 5  # seconds

LINE_PUBLISHING_PORT = '5556'


class Pi(Driver):
    """driver class for use with the Raspberry Pi

    connects to the display via serial and knows how to send and receive data
    to it

    :param port: the serial port the display is plugged into
    """

    def __init__(self, port=None, timeout=60, button_threshold=1):
        self.timeout = timeout
        self.button_threshold = button_threshold
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

        self.previous_buttons = dict()

        self.row_actuations = [0] * N_ROWS

        super(Pi, self).__init__()

    def setup_serial(self, port):
        """sets up the serial port with a timeout and flushes it.
        Timeout is set to 60s, as this is well beyond a full page refresh of
        the hardware

        :param port: the serial port the display is plugged into
        """
        try:
            serial_port = serial.Serial()
            serial_port.port = port
            serial_port.timeout = float(self.timeout)
            serial_port.baudrate = 9600
            try:
                serial_port.open()
            except OSError as e:
                # ioctl errors thrown on macOS in unit tests if opened on pty
                # without setting dsrdtr and rtscts to True (but port is open)
                log.warn('error opening serial port %s, ignoring', e)
            serial_port.flush()
            self.HDLC = simple_hdlc.HDLC(serial_port)
            return serial_port
        except IOError as e:
            log.error('check usb connection to arduino %s', e)
            self.restarting('no-connection')
            sys.exit(1)

    def is_ok(self):
        """checks the serial connection. There doesn't seem to be a specific
        method in pyserial so we're using getCD()"""
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
        """get button states

        :rtype: dict of elements either set to 'down' or 'up'
        """
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
        for i, n in enumerate(reversed(list('{:0>14b}'.format(read_buttons)))):
            name = mapping[str(i)]
            if n == '1':
                if name in self.previous_buttons:
                    self.previous_buttons[name] += 1
                else:
                    self.previous_buttons[name] = 1                
                if self.previous_buttons[name] == self.button_threshold:
                    buttons[name] = 'down'
            elif n == '0' and (name in self.previous_buttons):
                if self.previous_buttons[name] >= self.button_threshold:
                    buttons[name] = 'up'
                del self.previous_buttons[name]

        return buttons

    def send_error_sound(self):
        """make the hardware make an error sound"""
        log.debug('error sound')
        self.send_data(comms.CMD_SEND_ERROR)

    def send_ok_sound(self):
        """make the hardware make an ok sound"""
        log.debug('ok sound')
        self.send_data(comms.CMD_SEND_OK)

    def send_data(self, cmd, data=[]):
        """send data to the hardware

        :param cmd: command byte
        :param data: list of bytes
        """
        payload = struct.pack('%sb' % (len(data) + 1), cmd, *data)
        if self.port:
            if cmd == comms.CMD_SEND_LINE:
                row = data[0]
                self._log_row_actuation(row)
                self._publish_line(row, data[1:])

            self.HDLC.sendFrame(payload)

            if cmd == comms.CMD_RESET and not hasattr(self, 'context'):
                # defer this 'til after the initial reset is sent as it slows startup
                import zmq
                self.context = zmq.Context()
                self.socket = self.context.socket(zmq.PUB)
                self.socket.bind('tcp://*:%s' % LINE_PUBLISHING_PORT)

    def _publish_line(self, row, content):
        brl = ''.join([braille.pin_num_to_unicode(ch) for ch in content])
        brf = ''.join(braille.pin_nums_to_alphas(content))
        self.socket.send_pyobj(
            {'line_number': row, 'visual': brf, 'braille': brl})

    def restarting(self, reason):
        if hasattr(self, 'context'):
            self.socket.send_pyobj({'restarting': reason})

    async def async_get_data(self, expected_cmd):
        """gets 2 bytes of data from the hardware

        :param expected_cmd: what command we're expecting (error raised
        otherwise)

        :rtype: an integer return value
        """
        # 4s is roughly the max amount of time it takes to render a line.
        # The MCUs will reply instantly to a single SEND_LINE but when a second
        # is sent immediately after the first it'll be blocked (unacknowledged)
        # until the first completes.
        timeout_at = time.time() + 4
        # 5 bytes is the minimum HDLC frame: 0x7E,cmd,cksum,cksum,0x7E
        while self.port.inWaiting() < 5 and time.time() < timeout_at:
            await asyncio.sleep(0)

        if self.port.inWaiting() < 5:
            return -1

        return self.get_data(expected_cmd)

    def get_data(self, expected_cmd):
        """gets 2 bytes of data from the hardware

        :param expected_cmd: what command we're expecting (error raised
        otherwise)

        :rtype: an integer return value
        """
        try:
            self.HDLC.readFrame(4)
        except ValueError as e:
            # Got a frame but CRC incorrect.  Punt for now and see
            # where it lands, since this interface makes no allowance
            # for failure.
            raise e
        except OSError as e:
            # Input/output error
            raise e
        except RuntimeError as e:
            # No complete frame within timeout.  Same again.
            raise e
        message = self.HDLC.last_frame.data

        if len(message) < 2:
            log.warning('unexpected rx data length %d' % len(message))
        data = struct.unpack('3b', message)
        if data[0] != expected_cmd:
            log.warning('unexpected rx command %d, expecting %d' %
                        (data[0], expected_cmd))
        return data[1] | (data[2] << 8)

    async def track_duty(self):
        # FIXME: prefer to do this in constructor, but it breaks test_txrx
        self.i2c_bus = smbus2.SMBus(1)
        # Fetch any existing actuation counts from EEPROM.
        self._read_actuations()
        # Every 5 minutes, or when cancelled, save actuations back to
        # EEPROM.
        last_actuations = self.row_actuations
        try:
            while True:
                await asyncio.sleep(ACTUATION_SAVE_PERIOD)
                if self.row_actuations != last_actuations:
                    self._save_actuations()
                last_actuations = self.row_actuations
        except asyncio.CancelledError:
            self._save_actuations()
            raise

    def _save_actuations(self):
        """Update EEPROM with actuations from the last period"""
        # We loaded actuations from EEPROM so we can simply write.
        start_address = struct.pack('>H', DUTY_RECORD_ADDR)

        # Keep this to one page; store only the 24 lowest bits of each.
        data = b''.join([struct.pack('<I', count)[0:BYTES_PER_DUTY_RECORD]
                         for count in self.row_actuations])

        write = smbus2.i2c_msg.write(0x50, start_address + data)

        self.i2c_bus.i2c_rdwr(write)
        log.debug('Duty cycles written back to EEPROM')

    def _read_actuations(self):
        """Extract past actuations from EEPROM"""
        start_address = struct.pack('>H', DUTY_RECORD_ADDR)

        write = smbus2.i2c_msg.write(0x50, start_address)
        read = smbus2.i2c_msg.read(0x50, N_ROWS * BYTES_PER_DUTY_RECORD)

        self.i2c_bus.i2c_rdwr(write, read)

        read = bytes(list(read))
        for i in range(N_ROWS):
            first = BYTES_PER_DUTY_RECORD * i
            after = BYTES_PER_DUTY_RECORD * (i + 1)
            padded_record = read[first:after] + b'\0'
            saved_actuations = struct.unpack('<I', padded_record)[0]
            if saved_actuations != 0x00FFFFFF:
                # UI might have started rendering already, so add 'em up.
                self.row_actuations[i] += saved_actuations

    def _log_row_actuation(self, row):
        """Increment cached actuation count for :row:.
           Cache will be periodically written to EEPROM in background."""
        self.row_actuations[row] += 1

    def __exit__(self, ex_type, ex_value, tb):
        """__exit__ method allows us to shut down the port properly"""
        if ex_type is not None:
            log.error(traceback.format_exception(ex_type, ex_value, tb))
        if self.port:
            log.error('closing serial port')
            self.port.close()
        if hasattr(self, 'context'):
            self.context.destroy()
        if hasattr(self, 'button_thread'):
            self.button_thread.join()

    def __enter__(self):
        """method required for using the `with` statement"""
        return self


Driver.register(Pi)
