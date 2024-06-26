from collections import OrderedDict

from .book_file import LoadState
from ..manual import Manual, manual_filename
from ..i18n import DEFAULT_LOCALE
from ..braille import DEFAULT_ENCODING
from .. import state


manual = Manual.create()


class UserState:
    def __init__(self, root: 'state.RootState'):
        self.root = root
        self.current_book = manual_filename
        self.current_language = DEFAULT_LOCALE
        self.current_encoding = DEFAULT_ENCODING
        self.books = OrderedDict({manual_filename: manual})

    @property
    def book(self):
        return self.books[self.current_book]

    @property
    def successful_books(self):
        # should this be a (generator)?
        return [b for b in self.books.values() if b.load_state != LoadState.FAILED]

    def load(self, current_book, current_language, current_encoding):
        self.current_book = current_book
        if not self.current_book == manual_filename:
            self.root.app.library.show_files_dir(self.current_book)
        self.current_language = current_language
        self.current_encoding = current_encoding

    def go_to_start(self):
        self.set_book_page(0)

    def go_to_end(self):
        book = self.book
        last_page = book.get_num_pages() - 1
        self.set_book_page(last_page)

    def set_book_page(self, page):
        book = self.book

        # if user selects bookmark straight after deleting (rather than
        # closing menu) we may need to prune here
        bookmarks = book.bookmarks_pruned
        if bookmarks is not book.bookmarks:
            book = book._replace(bookmarks=bookmarks)

        book = book.set_page(page)
        self.books[self.current_book] = book

        self.root.app.location = 'book'
        self.root.app.home_menu_visible = False
        self.root.refresh_display()
        self.root.save_state(book)

    def enter_go_to_page(self):
        self.root.app.home_menu_visible = False
        self.root.app.location = 'go_to_page'
        self.root.refresh_display()

    def toggle_home_menu(self):
        self.root.app.home_menu_visible = not self.root.app.home_menu_visible
        self.root.refresh_display()

    def insert_bookmark(self):
        book = self.book
        page = book.page_number
        if page not in book.bookmarks:
            bookmarks = sorted(book.bookmarks + tuple([page]))
            book = book._replace(bookmarks=tuple(bookmarks))
            self.books[self.current_book] = book
            self.root.save_state(book)

    def to_file(self, media_dir):
        current_book = self.current_book
        return {
            'current_book': current_book,
            'current_language': self.current_language,
            'current_encoding': self.current_encoding
        }
