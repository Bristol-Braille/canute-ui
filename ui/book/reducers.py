from frozendict import FrozenOrderedDict
from collections import OrderedDict
from .. import state_helpers


class BookReducers():
    def go_to_start(self, state, value):
        return self.set_book_page(state, 0)

    def go_to_end(self, state, value):
        width, height = state_helpers.dimensions(state)
        book = state_helpers.get_current_book(state)
        last_page = book.get_num_pages() - 1
        return self.set_book_page(state, last_page)

    def set_book_page(self, state, page):
        width, height = state_helpers.dimensions(state)
        book_n = state['user']['current_book']
        books = OrderedDict(state['user']['books'])
        book = books[book_n].set_page(page)
        bookmarks = tuple(bm for bm in book.bookmarks if bm != 'deleted')
        book = book._replace(bookmarks=bookmarks)
        books[book_n] = book
        return state.copy(user=state['user'].copy(books=FrozenOrderedDict(books)),
                          location='book', home_menu_visible=False)

    def enter_go_to_page(self, state, value):
        return state.copy(home_menu_visible=False, location='go_to_page')

    def toggle_home_menu(self, state, value):
        return state.copy(home_menu_visible=not state['home_menu_visible'])

    def insert_bookmark(self, state, _):
        number = state['user']['current_book']
        books = OrderedDict(state['user']['books'])
        book = books[number]
        page = book.page_number
        if page not in book.bookmarks:
            bookmarks = sorted(book.bookmarks + tuple([page]))
            book = book._replace(bookmarks=tuple(bookmarks))
            books[number] = book
            return state.copy(user=state['user'].copy(books=FrozenOrderedDict(books)))
        return state
