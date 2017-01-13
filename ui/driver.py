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

    def reset_display(self):
        self.send_data(CMD_RESET)
        return self.get_data(CMD_RESET)

    def warm_up(self):
        self.send_data(CMD_WARMUP)
        return self.get_data(CMD_WARMUP)

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
        returns an object of the button states

        :rtype: object of the buttons  {id: state} where state is
        set to 'single', 'long' or 'double' (or the id is not present if
        unpressed)
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

        log.debug("setting page of braille:")

        for row in range(self.rows):
            row_braille = data[row*self.chars:row*self.chars+self.chars]
            self.set_braille_row(row, row_braille)

    def set_braille_row(self, row, data):
        if len(data) > self.chars:
            log.warning("row data too long, length %d, truncating to %d" % (len(data), self.chars))
            data = data[0:self.chars]

        log.debug("setting row of braille:")
        log.debug("row %i: |%s|" % (row, '|'.join(map(utility.pin_num_to_unicode, data))))

        self.send_data(CMD_SEND_LINE, [row] + list(data))

        # get status
        self.status = self.get_data(CMD_SEND_LINE)
        if self.status != 0:
            log.warning("got an error after setting braille: %d" % self.status)

    @staticmethod
    def _make_char(cell_data):
        """
        Translates a bitmapped list-of-lists to a braille cell number

        :type cell_data: List[List[int]]
        cell_data is assumed to be in the format [[A,B],[C,D],[E,F]], and each entry is a zero or non-zero.
        zero (=black) means pin should be raised.
        """

        return sum(((cell_data[y][x] == 0) * 2 ** (x * 3 + y)) for x in range(2) for y in range(3))

    def display_graphic(self, graphic_data):
        """
        displays a graphic, formatted as a rectangular list of list of the right size.

        :type graphic_data: List[List[int]]
        graphic_data is a list of lists of integers, representing a graphic to be displayed. The first list is the
        first row of pixels, and so on. A zero represents pin raised (=black). Any other number represents pin
        lowered (=white).
        """
        for row in range(self.rows):
            row_braille = [self._make_char([x[i * 2:(i + 1) * 2]
                                            for x in graphic_data[row * 3:(row + 1) * 3]])
                           for i in range(self.chars)]
            self.set_braille_row(row, row_braille)

    def load_graphic(self, fname):
        """
         loads and displays a graphic from a file.

         :type fname: basestring - path to the file to be opened.
         """
        from PIL import Image
        try:
            im = Image.open(fname)
        except IOError:
            log.error("Could not load graphics file: %s" % fname)
            return
        # reformat to right size and monochrome.
        # TODO: Add option to account for gaps between cells, preserving overall shapes.
        # (Would need much more detail on geometry of cell layout.)
        canvas_width = self.chars * 2
        canvas_height = self.rows * 3
        gray = im.convert('L')
        bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
        bw.thumbnail((canvas_width, canvas_height))
        pixels = list(bw.getdata())
        width, height = bw.size
        pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
        pixels = [a + [255] * (canvas_width - width) for a in pixels] \
                 + [[255] * canvas_width] * (canvas_height - height)
        self.display_graphic(pixels)
        # To save the scaled/formatted graphic for debugging purposes:
        # bw.save('debug.png')
