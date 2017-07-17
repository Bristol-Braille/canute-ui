import logging
from . import utility
from .library import view as library_view
from .system_menu import view as system_menu_view


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
            page_data = system_menu_view.render(width, height, state['system_menu'])
            self._set_buffer(page_data)
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
