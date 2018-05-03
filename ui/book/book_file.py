import os
from collections import namedtuple
from enum import Enum
import logging


log = logging.getLogger(__name__)


class LoadState(Enum):
    INITIAL = 0
    LOADING = 1
    DONE = 2


BookData = namedtuple('BookData', ['filename', 'width', 'height',
                                   'page_number', 'bookmarks',
                                   'file_contents', 'pages', 'load_state'])
BookData.__new__.__defaults__ = (None, None, None,
                                 0, tuple(),
                                 None, tuple(), LoadState.INITIAL)


class BookFile(BookData):
    @property
    def ext(self):
        return os.path.splitext(self.filename)[-1].lower()

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    @property
    def max_pages(self):
        if self.load_state != LoadState.DONE:
            return -1
        m = len(self.pages) - 1
        if m < 0:
            return 0
        return m

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page > self.max_pages:
            page = self.max_pages
        return self._replace(page_number=page)
