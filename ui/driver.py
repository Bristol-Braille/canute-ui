import logging
log = logging.getLogger(__name__)
from comms_codes import *
import abc
import utility

class DriverError(Exception):
    pass


class Driver(object):
    '''Abstract base class of the braille device's capabilities.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.status = 0
        (self.chars, self.rows) = self.get_dimensions()
        self.page_length = self.rows * self.chars
        log.info("device ready with %d x %d characters" % (self.chars, self.rows))

    @abc.abstractmethod
    def is_ok(self):
        '''checks the display is online
        :rtype: True or False
        '''
        return

    @abc.abstractmethod
    def send_error_sound(self):
        '''make the hardware make an error sound'''
        return

    @abc.abstractmethod
    def send_ok_sound(self):
        '''make the hardware make an ok sound'''
        return

    @abc.abstractmethod
    def get_data(self, expected_cmd):
        return

    @abc.abstractmethod
    def send_data(self, cmd, data=[]):
        return

    def get_dimensions(self):
        '''
        returns dimensions of the display

        :rtype: a tuple containing 2 integers: number of cells and number of
        rows
        '''
        self.send_data(CMD_GET_CHARS)
        chars = self.get_data(CMD_GET_CHARS)
        self.send_data(CMD_GET_ROWS)
        rows = self.get_data(CMD_GET_ROWS)
        return (chars, rows)

    def get_page_length(self):
        '''
        returns length of data required to fill a full page

        :rtype: an integer
        '''
        return self.page_length

    def clear_page(self):
        data = [0] * self.page_length
        self.set_braille(data)

    @abc.abstractmethod
    def get_buttons(self):
        '''
        returns a list of the 8 button states

        :rtype: list of 8 elements either set to 'single', 'long' or 'double'
        (pressed) or False (unpressed)
        '''
        return

    def set_braille(self, data):
        '''send braille data to the display
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

        '''
        if len(data) > self.page_length:
            log.warning("page data too long, length %d, truncating to %d" % (len(data), self.page_length))
            data = data[0:self.page_length]

        log.debug("setting page of braille:")
        for row in range(self.rows):
            row_braille = data[row*self.chars:row*self.chars+self.chars]
            log.debug("row %i: |%s|" % (row, '|'.join(map(utility.pin_num_to_unicode, row_braille))))

        self.send_data(CMD_SEND_DATA, data)

        # get status
        self.status = self.get_data(CMD_SEND_DATA)
        if self.status != 0:
            raise DriverError("got an error after setting braille: %d" % self.status)

    def set_braille_row(self, row, data):
        if len(data) > self.chars:
            log.warning("row data too long, length %d, truncating to %d" % (len(data), self.chars))
            data = data[0:self.chars]

        log.debug("setting row of braille:")
        log.debug("row %i: |%s|" % (row, '|'.join(map(utility.pin_num_to_unicode, data))))

        self.send_data(CMD_SEND_LINE, [row] + data)

        # get status
        self.status = self.get_data(CMD_SEND_LINE)
        if self.status != 0:
            raise DriverError("got an error after setting braille: %d" % self.status)
