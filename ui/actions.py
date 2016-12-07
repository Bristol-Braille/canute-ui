import os
import pydux
from frozendict import frozendict

import logging
log = logging.getLogger(__name__)

import utility
from functools import partial

class Reducers():
    def init(self, _, state):
        return state
    def go_to_book(self, state, number):
        width, height = dimensions(state)
        page = state['library']['page']
        line_number = page * (height - 1)
        try:
            location = state['books'][line_number + number]
        except:
            log.warning('no book at {}'.format(number))
            return state
        return state.copy(location = line_number + number)
    def go_to_library(self, state, value):
        return state.copy(location = 'library')
    def go_to_menu(self, state, value):
        return state.copy(location = 'menu')
    def set_books(self, state, books):
        width, height = dimensions(state)
        books = map(lambda b: {'data': b, 'page':0}, books)
        books = sort_books(books)
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        library = frozendict({'data': tuple(data), 'page': 0})
        return state.copy(location = 'library', books = tuple(books), library = library)
    def add_book(self, state, book_data):
        width, height = dimensions(state)
        book = {'data': book_data, 'page':0}
        books = list(state['books'])
        books.append(book)
        books = sort_books(books)
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        page = state['library']['page']
        library = frozendict({'data': data, 'page': page})
        return state.copy(books = tuple(books), library = library)
    def remove_book(self, state, filename):
        width, height = dimensions(state)
        books = filter(lambda b: b['data'].filename != filename, state['books'])
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        maximum = get_max_pages(data, height)
        page = state['library']['page']
        if page > maximum:
            page = maximum
        library = frozendict({'data': data, 'page': page})
        return state.copy(books = tuple(books), library = library)
    def next_page(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page    = state['library']['page'] + 1
            library = set_page(library, page, (height - 1))
            return state.copy(library = library)
        elif type(location) == int:
            book = state['books'][location]
            data = book['data']
            page = book['page'] + 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return state.copy(books = tuple(books))
        return state
    def previous_page(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page    = library['page'] - 1
            library = set_page(library, page, (height - 1))
            return state.copy(library = library)
        elif type(location) == int:
            book = state['books'][location]
            data = book['data']
            page = book['page'] - 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return state.copy(library = tuple(books))
        return state
    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress':
            return state
        else:
            return state.copy(replacing_library = value)
    def backup_log(self, state, value):
        if state['backing_up_log'] == 'in progress':
            return state
        else:
            return state.copy(backing_up_log = value)
    def shutdown(self, state, value):
        return state.copy(shutting_down = True)


def sort_books(books):
    return sorted(books, key=lambda book: book['data'].filename)


def dimensions(state):
    width = state['display']['width']
    height = state['display']['height']
    return [width, height]


def get_title(book):
    basename = os.path.basename(book['data'].filename)
    title = os.path.splitext(basename)[0]
    return utility.alphas_to_pin_nums(title)


def set_page(book, page, height):
    data = book['data']
    if page < 0 or page > get_max_pages(data, height):
        return book
    else:
        return frozendict({'data': data, 'page': page})


def get_max_pages(data, height):
    return len(data) // height


def make_action_method(name):
    '''Returns a method that returns a dict to be passed to dispatch'''
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


action_types = utility.get_methods(Reducers)
#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))

