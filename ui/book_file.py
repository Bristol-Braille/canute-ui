import os
from collections import namedtuple
import logging


log = logging.getLogger(__name__)


BookData = namedtuple(
    'BookData', 'filename width height page_number bookmarks file_contents pages loading')
BookData.__new__.__defaults__ = (
    None, None, None, 0, tuple(), None, None, False)


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
        return len(self.pages) - 1

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page > self.max_pages:
            page = self.max_pages
        return self._replace(page_number=page)
