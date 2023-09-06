from frozendict import FrozenOrderedDict
import logging
from collections import OrderedDict

from ..book import book_file
from .. import state_helpers

log = logging.getLogger(__name__)


class LibraryReducers():
    def go_to_book(self, state, number):
        width, height = state_helpers.dimensions(state)
        page = state['library']['page']
        line_number = page * (height - 1)
        books = state_helpers.get_books(state)
        try:
            book = books[line_number + number]
        except Exception:
            log.debug('no book at {}'.format(number))
            return state
        user = state['user'].set('current_book', book.filename)
        new_state = state.set('location', 'book')
        new_state = new_state.set('user', user)
        return new_state.set('home_menu_visible', False)

    def add_or_replace(self, state, book):
        books = OrderedDict(state['user']['books'])
        books[book.filename] = book
        books = sort_books(books)
        return state.set('user', state['user'].set('books', books))

    def set_book_loading(self, state, book):
        book = book._replace(load_state=book_file.LoadState.LOADING)
        return self.add_or_replace(state, book)

    def remove_book(self, state, book):
        books = OrderedDict(state['user']['books'])
        if book.filename in books:
            del books[book.filename]
        books = FrozenOrderedDict(books)
        return state.set('user', state['user'].set('books', books))

    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress' and value is False:
            return state
        else:
            new_state = state.set('replacing_library', value)
            return new_state.set('location', 'library')


def sort_books(books):
    return FrozenOrderedDict(sorted(books.items(), key=lambda x: x[1].title.lower()))
