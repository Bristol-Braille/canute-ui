import os
from collections import namedtuple, OrderedDict
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
                                   'indexed', 'pages', 'load_state',
                                   'num_pages'])
BookData.__new__.__defaults__ = (None, None, None,
                                 0, tuple([0]),
                                 None, tuple(), LoadState.INITIAL,
                                 0)


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
    def bookmarks_pruned(self):
        if 'deleted' in self.bookmarks:
            return tuple(bm for bm in self.bookmarks if bm != 'deleted')
        else:
            return self.bookmarks

    def get_num_pages(self):
        if self.load_state != LoadState.DONE:
            log.warning('get pages on not-yet-loaded book')
        if self.indexed:
            return self.num_pages
        else:
            return len(self.pages)

    @property
    def page_num_width(self):
        return len(str(self.get_num_pages()))

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page >= self.get_num_pages():
            page = self.get_num_pages() - 1
        return self._replace(page_number=page)

    def to_file(self):
        # remove deleted, start-of-book and end-of-book bookmarks
        bms = self.bookmarks_pruned[1:-1]
        # ordered to make sure current_page comes before bookmarks
        return OrderedDict([
            ['current_page', self.page_number + 1],
            ['bookmarks', list(bms)]
        ])

    def relpath(self, media_dir):
        return os.path.relpath(self.filename, start=media_dir)
