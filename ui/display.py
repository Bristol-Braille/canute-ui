import logging
from . import utility


log = logging.getLogger(__name__)


class Display():
    def __init__(self):
        self.row = 0
        self.hardware_state = []
        self.buffer = []

    def render_to_buffer(self, state):
        width, height = utility.dimensions(state)
        location = state['location']
        if location == 'library':
            page = state['library']['page']
            data = state['library']['data']
            # subtract title from page height
            data_height = height - 1
            max_pages = utility.get_max_pages(data, data_height)
            n = page * data_height
            data = data[n: n + data_height]
            # pad page with empty rows
            while len(data) < data_height:
                data += ((0,) * width,)
            title = format_title('library menu', width, page, max_pages)
            self._set_buffer(tuple([title]) + tuple(data))
        elif location == 'menu':
            page = state['menu']['page']
            data = state['menu']['data']
            # subtract title from page height
            data_height = height - 1
            max_pages = utility.get_max_pages(data, data_height)
            title = format_title('system menu', width, page, max_pages)
            n = page * data_height
            data = data[n: n + data_height]
            # pad page with empty rows
            while len(data) < data_height:
                data += ((0,) * width,)
            self._set_buffer(tuple([title]) + tuple(data))
        elif type(location) == int:
            page = state['books'][location]['page']
            data = state['books'][location]['data']
            n = page * height
            data = data[n: n + height]
            self._set_buffer(data)

    def send_line(self, driver):
        row = self.row
        if row >= len(self.buffer):
            return
        while row >= len(self.hardware_state):
            self.hardware_state.append([])
        braille = self.buffer[row]
        if braille != self.hardware_state[row]:
            driver.set_braille_row(row, braille)
            self.hardware_state[row] = braille
        self.row += 1

    def _set_buffer(self, data):
        self.buffer = data
        self.row = 0


def format_title(title, width, page_number, total_pages):
    '''
    format a title like this:
        * title on the top line.
        * use two dot-six characters to indicate all uppercase for the title.
        * page numbers all the way at the right with 3 digits out of total,
        e.g. 001 / 003.
    '''
    # hack - leave space at the beginning for the uppercase symbols
    uppercase = '  '
    title = '%s%s' % (uppercase, title)
    current_page = ' %03d / %03d' % (page_number + 1, total_pages + 1)

    available_title_space = width - len(current_page)

    # make title right length
    if len(title) > available_title_space:
        # truncate
        title = title[0:available_title_space]
    else:
        # pad
        title += ' ' * (available_title_space - len(title))

    title_pins = utility.alphas_to_pin_nums(title + current_page)
    # replace first 2 chars with the uppercase symbols
    title_pins[0:2] = [32, 32]
    return title_pins
