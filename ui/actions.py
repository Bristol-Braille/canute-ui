import os
import pydux
from pydux.extend import extend

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
        line_number = page * height
        try:
            location = state['books'][line_number + number]
        except:
            log.warning('no book at {}'.format(number))
            return state
        return extend(state, {'location': line_number + number})
    def go_to_library(self, state, value):
        return extend(state, {'location': 'library'})
    def go_to_menu(self, state, value):
        return extend(state, {'location': 'menu'})
    def set_books(self, state, books):
        width, height = dimensions(state)
        books = map(lambda b: {'data': b, 'page':0}, books)
        books = sort_books(books)
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        library = {'data': data, 'page': 0}
        return extend(state, {'location': 'library', 'books': tuple(books), 'library': library})
    def next_page(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page    = state['library']['page'] + 1
            library = set_page(library, page, height)
            return extend(state, {'library': library})
        elif type(location) == int:
            book = state['books'][location]
            data = book['data']
            page = book['page'] + 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return extend(state, {'books': tuple(books)})
        return state
    def previous_page(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page    = library['page'] - 1
            library = set_page(library, page, height)
            return extend(state, {'library': library})
        elif type(location) == int:
            book = state['books'][location]
            data = book['data']
            page = book['page'] - 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return extend(state, {'books': tuple(books)})
        return state
    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress':
            return state
        else:
            return extend(state, {'replacing_library': value})
    def shutdown(self, state, value):
        return extend(state, {'shutting_down': True})
    def backup_log(self, state, value):
        if state['backing_up_log'] == 'in progress':
            return state
        else:
            return extend(state, {'backing_up_log': value})


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
        return {'data': data, 'page': page}


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

