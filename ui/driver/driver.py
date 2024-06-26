import logging
import abc
from . import comms_codes as comms


log = logging.getLogger(__name__)


class DriverError(Exception):
    pass


class Driver(object, metaclass=abc.ABCMeta):
    """Abstract base class of the braille device's capabilities.
    """

    def __init__(self):
        self.status = 0
        (self.chars, self.rows) = self.get_dimensions()
        self.page_length = self.rows * self.chars
        log.info('device ready with %d x %d characters' %
                 (self.chars, self.rows))

    @abc.abstractmethod
    def is_ok(self):
        """checks the display is online
        :rtype: True or False
        """
        return

    @abc.abstractmethod
    def send_error_sound(self):
        """make the hardware make an error sound"""
        return

    @abc.abstractmethod
    def send_ok_sound(self):
        """make the hardware make an ok sound"""
        return

    @abc.abstractmethod
    def get_data(self, expected_cmd):
        return

    @abc.abstractmethod
    def send_data(self, cmd, data=[]):
        return

    def restarting(self, reason):
        # indicates we're starting a restart to reset the display / re-read
        # data / reconnect after timeout
        return

    @abc.abstractmethod
    async def async_get_data(self, cmd, data=[]):
        return

    async def track_duty(self):
        # Pi driver periodically saves actuations to EEPROM.
        return

    def reset_display(self):
        self.send_data(comms.CMD_RESET)
        return self.get_data(comms.CMD_RESET)

    def warm_up(self):
        self.send_data(comms.CMD_WARMUP)
        return self.get_data(comms.CMD_WARMUP)

    def lower_rods(self):
        self.send_data(comms.CMD_LOWER)
        # Work around due to response not being received when we try
        return True

    def get_dimensions(self):
        """
        returns dimensions of the display

        :rtype: a tuple containing 2 integers: number of cells and number of
        rows
        """
        self.send_data(comms.CMD_GET_CHARS)
        chars = self.get_data(comms.CMD_GET_CHARS)
        self.send_data(comms.CMD_GET_ROWS)
        rows = self.get_data(comms.CMD_GET_ROWS)
        return (chars, rows)

    def get_page_length(self):
        """
        returns length of data required to fill a full page

        :rtype: an integer
        """
        return self.page_length

    def clear_page(self):
        data = [0] * self.page_length
        self.set_braille(data)

    @abc.abstractmethod
    def get_buttons(self):
        """
        returns an object of the button states

        :rtype: object of the buttons  {id: state} where state is
        set to 'single', 'long' or 'double' (or the id is not present if
        unpressed)
        """
        return

    def set_braille(self, data):
        """send braille data to the display
        each cell is represented by a number from 0 to 63:

        .. code-block:: none

                 1 . . 4
           0  =  2 . . 5
                 3 . . 6

                 1 o . 4
           1  =  2 . . 5
                 3 . . 6

                 1 . . 4
           2  =  2 o . 5
                 3 . . 6

                 1 o . 4
           3  =  2 o . 5
                 3 . . 6

                 1 . . 4
           4  =  2 . . 5
                 3 o . 6

           ...

                 1 o o 4
           63 =  2 o o 5
                 3 o o 6

        :param data: a list of cells. The length of data will be cells * rows
        as returned by :func:`get_dimensions`

        """

        log.debug('setting page of braille:')

        for row in range(self.rows):
            row_braille = data[row * self.chars:row * self.chars + self.chars]
            self.set_braille_row(row, row_braille)

    def set_braille_row(self, row, data):
        if len(data) < self.chars:
            data = tuple(data) + ((0,) * (self.chars - len(data)))

        if len(data) > self.chars:
            data = data[0:self.chars]

        self.send_data(comms.CMD_SEND_LINE, [row] + list(data))

        self.status = self.get_data(comms.CMD_SEND_LINE)
        if self.status != 0:
            log.warning('got an error after setting braille: %d' % self.status)

    def is_motion_complete(self):
        flags = self._poll()
        return flags & (1 << comms.POLL_FLAG_BIT_MOVING) == 0

    def _poll(self):
        self.send_data(comms.CMD_POLL)
        return self.get_data(comms.CMD_POLL)

    async def async_set_braille_row(self, row, data):
        if len(data) < self.chars:
            data = tuple(data) + ((0,) * (self.chars - len(data)))

        if len(data) > self.chars:
            data = data[0:self.chars]

        self.send_data(comms.CMD_SEND_LINE, [row] + list(data))

        self.status = await self.async_get_data(comms.CMD_SEND_LINE)
        return self.status
