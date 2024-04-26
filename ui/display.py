import logging
from .config_loader import import_pages


log = logging.getLogger(__name__)


page_views = import_pages('view')

class Display():
    def __init__(self):
        self.row = 0
        self.hardware_state = []
        self.buffer = []
        self.up_to_date = True

    async def render_to_buffer(self, state):
        width, height = state.app.dimensions
        location = state.app.location
        try:
            page_data = await page_views[location].render(width, height, state)
            self._set_buffer(page_data)
        except:
            log.warn('unknown page location')

    async def send_line(self, driver):
        row = self.row
        if row >= len(self.buffer):
            self.up_to_date = True
            return
        self.row += 1
        while row >= len(self.hardware_state):
            self.hardware_state.append([])
        braille = self.buffer[row]
        failure_status = 0
        warm_reset = False
        while braille != self.hardware_state[row]:
            status = await driver.async_set_braille_row(row, braille)
            if status != 0:
                if failure_status == 0:
                    log.warning(
                        'line send failed with status %d, retrying' % status)
                failure_status = status
                # FIXME: Horrible to have an unnamed constant here.
                # This is REPLY_WARM_RESET, but, should display really
                # be importing protocol constants?  Or, should driver
                # really be translating protocol constants into
                # corresponding driver failure codes?
                if not warm_reset and status == 0xDD:
                    warm_reset = True
                    log.warning(
                        'line refused because motors busy doing warm reset')
            else:
                if warm_reset:
                    # If we waited out a warm reset, invalidate display
                    # cache.
                    self.hardware_state = []
                    while row >= len(self.hardware_state):
                        self.hardware_state.append([])
                self.hardware_state[row] = braille
                if warm_reset:
                    # If we waited out a warm reset, flag that we need
                    # to refresh all other lines.
                    self.row = 0
                    self.up_to_date = False
                if failure_status != 0:
                    log.warning('overcame line send error')

    def is_up_to_date(self):
        return self.up_to_date

    def _set_buffer(self, data):
        if data != self.buffer:
            self.buffer = data
            self.up_to_date = False
        self.row = 0
