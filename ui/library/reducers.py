from frozendict import frozendict
import logging
from functools import partial

from .. import utility
from ..braille import from_ascii
from ..manual import manual_filename

log = logging.getLogger(__name__)


class LibraryReducers():
    def go_to_book(self, state, number):
        width, height = utility.dimensions(state)
        page = state['library']['page']
        line_number = page * (height - 1)
        try:
            state['user']['books'][line_number + number]
        except:
            log.warning('no book at {}'.format(number))
            return state
        user = state['user'].copy(book=line_number + number)
        return state.copy(location='book', user=user, home_menu_visible=False)

    def set_book(self, state, n):
        return state.copy(book=n)

    def set_books(self, state, books):
        width, height = utility.dimensions(state)
        books = tuple(sort_books(books))
        data = list(map(lambda b: from_ascii(b.title), books))
        data = list(map(partial(utility.pad_line, width), data))
        library = frozendict({'data': tuple(data), 'page': 0})
        return state.copy(location='library',
                          user=state['user'].copy(book=0, books=books), library=library)

    def add_book(self, state, book):
        book_filenames = (b.filename for b in state['user']['books'])
        if book.filename in book_filenames:
            return state
        width, height = utility.dimensions(state)
        books = list(state['user']['books'])
        books.append(book)
        books = sort_books(books)
        return state.copy(user=state['user'].copy(books=tuple(books)))

    def add_books(self, state, books_to_add):
        for book in books_to_add:
            state = self.add_book(state, book)
        return state

    def add_or_replace(self, state, book):
        books = state['user']['books']
        books = list(filter(lambda b: b.filename != book.filename, books))
        books.append(book)
        books = sort_books(books)
        return state.copy(user=state['user'].copy(books=tuple(books)))

    def set_book_loading(self, state, book):
        book = book._replace(loading=True)
        return self.add_or_replace(state, book)

    def remove_books(self, state, filenames):
        filenames = [f for f in filenames if f != manual_filename]
        width, height = utility.dimensions(state)
        books = [
            b for b in state['user']['books'] if b.filename not in filenames
        ]
        maximum = (len(books) - 1) // (height - 1)
        library = state['library']
        if library['page'] > maximum:
            library = library.copy(page=maximum)
        return state.copy(user=state['user'].copy(books=tuple(books)), library=library)

    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress' and value != False:
            return state
        else:
            return state.copy(replacing_library=value, location='library')


def sort_books(books):
    return sorted(books, key=lambda book: book.title.lower())
