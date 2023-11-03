import logging
from collections import OrderedDict

from ..book import book_file
from .. import state


log = logging.getLogger(__name__)


class LibraryState:
    def __init__(self, root: 'state.RootState'):
        self.root = root

        self.page = 0
        self.dirs = []
        # index of directory that is currently expanded, if any
        self.files_dir_index = None
        self.files_count = 0

    @property
    def dir_count(self):
        return len(self.dirs)

    @property
    def open_dir(self):
        return self.dirs[self.files_dir_index] if self.files_page_open else None

    @property
    def files_page_open(self):
        return self.files_dir_index is not None

    def go_to_book(self, number):
        width, height = self.root.app.dimensions
        page = self.page
        line_number = page * (height - 1)
        books = self.root.app.user.successful_books
        try:
            book = books[line_number + number]
        except Exception:
            log.debug('no book at {}'.format(number))
            return
        self.root.app.user.current_book = book.filename
        self.root.app.location = 'book'
        self.root.app.home_menu_visible = False
        self.root.refresh_display()
        self.root.save_state()

    def add_or_replace(self, book):
        self.root.app.user.books[book.filename] = book
        books = sort_books(self.root.app.user.books)
        self.root.app.user.books = books

    def set_book_loading(self, book):
        book = book._replace(load_state=book_file.LoadState.LOADING)
        return self.add_or_replace(book)


def sort_books(books):
    return OrderedDict(sorted(books.items(), key=lambda x: x[1].title.lower()))
