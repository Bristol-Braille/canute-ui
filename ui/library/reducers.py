from frozendict import FrozenOrderedDict
import logging
from collections import OrderedDict

from .. import utility

log = logging.getLogger(__name__)


class LibraryReducers():
    def go_to_book(self, state, number):
        width, height = utility.dimensions(state)
        page = state['library']['page']
        line_number = page * (height - 1)
        books = tuple(state['user']['books'].values())
        try:
            book = books[line_number + number]
        except:
            log.warning('no book at {}'.format(number))
            return state
        user = state['user'].copy(current_book=book.filename)
        return state.copy(location='book', user=user, home_menu_visible=False)

    def add_or_replace(self, state, book):
        books = OrderedDict(state['user']['books'])
        books[book.filename] = book
        books = sort_books(books)
        return state.copy(user=state['user'].copy(books=books))

    def set_book_loading(self, state, book):
        book = book._replace(loading=True)
        return self.add_or_replace(state, book)

    def remove_book(self, state, book):
        books = OrderedDict(state['user']['books'])
        if book.filename in books:
            del books[book.filename]
        books = FrozenOrderedDict(books)
        return state.copy(user=state['user'].copy(books=books))

    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress' and value is False:
            return state
        else:
            return state.copy(replacing_library=value, location='library')


def sort_books(books):
    return FrozenOrderedDict(sorted(books.items(), key=lambda x: x[1].title.lower()))
