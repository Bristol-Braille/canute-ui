import logging
from . import utility
from .library import view as library_view


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
            page_data = library_view.render(width, height, state['library'])
            self._set_buffer(page_data)
        elif location == 'system_menu':
            page = state['system_menu']['page']
            data = state['system_menu']['data']
            # subtract title from page height
            data_height = height - 1
            max_pages = utility.get_max_pages(data, data_height)
            title = utility.format_title('system menu', width, page, max_pages)
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
