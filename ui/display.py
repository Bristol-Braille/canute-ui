import logging
import asyncio
from . import state_helpers
from .library import view as library_view
from .system_menu import view as system_menu_view
from .go_to_page import view as go_to_page_view
from .language import view as language_view
from .book import view as book_view
from .bookmarks import view as bookmarks_view


log = logging.getLogger(__name__)


class Display():
    def __init__(self):
        self.row = 0
        self.hardware_state = []
        self.buffer = []

    async def render_to_buffer(self, state, store):
        width, height = state_helpers.dimensions(state)
        location = state['location']
        if location == 'library':
            page_data = library_view.render(width, height, state)
            self._set_buffer(page_data)
        elif location == 'system_menu':
            page_data = system_menu_view.render(width, height, state)
            self._set_buffer(page_data)
        elif location == 'go_to_page':
            page_data = go_to_page_view.render(width, height, state)
            self._set_buffer(page_data)
        elif location == 'language':
            page_data = language_view.render(width, height, state)
            self._set_buffer(page_data)
        elif location == 'book':
            page_data = await book_view.render(width, height, state, store)
            self._set_buffer(page_data)
        elif location == 'bookmarks_menu':
            page_data = await bookmarks_view.render(width, height, state, store)
            self._set_buffer(page_data)

    async def send_line(self, driver):
        row = self.row
        if row >= len(self.buffer):
            return
        self.row += 1
        while row >= len(self.hardware_state):
            self.hardware_state.append([])
        braille = self.buffer[row]
        if braille != self.hardware_state[row]:
            await driver.async_set_braille_row(row, braille)
            # Don't issue new motions until current is done, but allow
            # button checks while we wait.
            while True:
                await asyncio.sleep(0.05)
                complete = await driver.is_motion_complete()
                if complete:
                    break
            self.hardware_state[row] = braille

    def _set_buffer(self, data):
        self.buffer = data
        self.row = 0
