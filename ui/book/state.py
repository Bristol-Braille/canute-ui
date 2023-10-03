from collections import OrderedDict

from .book_file import LoadState
from ..manual import Manual, manual_filename
from ..i18n import DEFAULT_LOCALE


manual = Manual.create()


class UserState:
    def __init__(self, root):
        self.root = root
        self.current_book = manual_filename
        # should default be en_GB:en ??
        self.current_language = DEFAULT_LOCALE.code
        self.books = OrderedDict({manual_filename: manual})

    @property
    def book(self):
        return self.books[self.current_book]

    @property
    def successful_books(self):
        # should this be a (generator)?
        return [b for b in self.books if b.load_state != LoadState.FAILED]

    def go_to_start(self):
        self.set_book_page(0)

    def go_to_end(self):
        book = self.book
        last_page = book.get_num_pages() - 1
        self.set_book_page(last_page)

    def set_book_page(self, page):
        book = self.book
        book.set_page(page)

        bookmarks = tuple(bm for bm in book.bookmarks if bm != 'deleted')
        book = book._replace(bookmarks=bookmarks)
        self.books[self.current_book] = book

        self.root.app.location = 'book'
        self.root.app.home_menu_visible = False
        # trigger redraw

    def enter_go_to_page(self):
        self.root.app.home_menu_visible = False
        self.root.app.location = 'go_to_page'
        # trigger redraw

    def toggle_home_menu(self):
        self.root.app.home_menu_visible = not self.root.app.home_menu_visible
        # trigger redraw

    def insert_bookmark(self, state, _):
        book = self.book
        page = book.page_number
        if page not in book.bookmarks:
            bookmarks = sorted(book.bookmarks + tuple([page]))
            book = book._replace(bookmarks=tuple(bookmarks))
            self.books[self.current_book] = book

