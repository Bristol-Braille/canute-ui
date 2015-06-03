import logging
import time
error_codes = []
log = logging.getLogger(__name__)
from comms_codes import *


class DriverError(Exception):
    pass


class Driver():
    '''
    abstracts the braille device's capabilities. Maybe should be a super class of hardware and hardware_emulated?

    :param hardware: the object used to communicate with the display. Object is either  :class:`.Hardware` or :class:`.HardwareEmulator`.
    '''

    def __init__(self, hardware):
        self.hardware = hardware
        self.status = 0
        (self.rows, self.chars) = self.get_dimensions()
        self.page_length = self.rows * self.chars

        log.info("device ready with %d x %d characters" % (self.chars, self.rows))

    def is_ok(self):
        '''checks the display is online
        :rtype: True or False
        '''
        return self.hardware.is_ok()

    def send_error_sound(self):
        '''make the hardware make an error sound'''
        log.debug("error sound")
        self.hardware.send_data(CMD_SEND_ERROR)

    def send_ok_sound(self):
        '''make the hardware make an ok sound'''
        log.debug("ok sound")
        self.hardware.send_data(CMD_SEND_OK)

    def get_status(self):
        '''return current status of canute hardware
        0 is OK, any other number should be looked up with :func:`get_error_codes`

        :rtype: an integer
        '''
        return self.status

    def get_dimensions(self):
        '''
        returns dimensions of the display

        :rtype: a tuple containing 2 integers: number of cells and number of rows
        '''
        self.hardware.send_data(CMD_GET_CHARS)
        chars = self.hardware.get_data(CMD_GET_CHARS)
        self.hardware.send_data(CMD_GET_ROWS)
        rows = self.hardware.get_data(CMD_GET_ROWS)
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

    def get_error_codes(self):
        '''return a list of human readable error codes

        :rtype: a list of string
        '''
        return error_codes

    def get_button_status(self):
        '''
        returns a list of the 8 button states

        :rtype: list of 8 elements either set to 'single', 'long' or 'double' (pressed) or False (unpressed)
        '''
        return self.hardware.get_buttons()

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

        :param data: a list of cells. The length of data will be cells * rows as returned by :func:`get_dimensions`
        '''
        if len(data) != self.page_length:
            raise DriverError("data incorrect length %d, should be %d" % (len(data), self.page_length))
        self.hardware.send_data(CMD_SEND_DATA, data)

        # get status
        self.status = self.hardware.get_data(CMD_SEND_DATA)
        if self.status != 0:
            raise DriverError("got an error after setting braille: %d" % self.status)

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

    with HardwareEmulator() as hardware:
        driver = Driver(hardware)
        driver.set_braille([0] * 28 * 4)
