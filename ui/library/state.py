import logging
from collections import OrderedDict

from ..book import book_file


log = logging.getLogger(__name__)


class LibraryState:
    def __init__(self, root):
        self.root = root
        self.page = 0

    def go_to_book(self, number):
        width, height = self.root.dimensions
        page = self.page
        line_number = page * (height - 1)
        books = self.root.user.successful_books
        try:
            book = books[line_number + number]
        except Exception:
            log.debug('no book at {}'.format(number))
            return
        self.root.user.current_book = book.filename
        self.root.location = 'book'
        self.root.home_menu_visible = False
        # trigger redraw

    def add_or_replace(self, state, book):
        self.root.user.books[book.filename] = book
        books = sort_books(books)
        self.root.user.books = books

    def set_book_loading(self, state, book):
        book = book._replace(load_state=book_file.LoadState.LOADING)
        return self.add_or_replace(state, book)

def sort_books(books):
    return OrderedDict(sorted(books.items(), key=lambda x: x[1].title.lower()))
