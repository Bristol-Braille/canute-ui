import os
from collections import namedtuple
from enum import Enum
import logging


log = logging.getLogger(__name__)


class LoadState(Enum):
    INITIAL = 0
    LOADING = 1
    DONE = 2
    FAILED = 3


BookData = namedtuple('BookData', ['filename', 'width', 'height',
                                   'page_number', 'bookmarks',
                                   'file_contents', 'pages', 'load_state'])
BookData.__new__.__defaults__ = (None, None, None,
                                 0, tuple([0]),
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

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page >= len(self.pages):
            page = len(self.pages) - 1
        return self._replace(page_number=page)
