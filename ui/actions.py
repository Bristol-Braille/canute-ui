import os
import pydux
from pydux.extend import extend

import logging
log = logging.getLogger(__name__)

import utility
from functools import partial
from bookfile_list import BookFile_List

def dimensions(state):
    width = state['display']['width']
    height = state['display']['height']
    return [width, height]


def get_title(book):
    return utility.alphas_to_pin_nums(os.path.basename(book['data'].filename))


def set_page(book, page, height):
    data = book['data']
    if page < 0 or page > get_max_pages(data, height):
        return book
    else:
        return {'data': data, 'page': page}


def get_max_pages(data, height):
    return len(data) // height


class Reducers():
    @staticmethod
    def go_to_book(state, action):
        width, height = dimensions(state)
        page = state['library']['page']
        line_number = page * height
        try:
            location = state['books'][line_number + action['value']]
        except:
            log.warning('no book at {}'.format(action['value']))
            return state
        return extend(state, {'location': line_number + action['value']})
    @staticmethod
    def go_to_library(state, action):
        return extend(state, {'location': 'library'})
    @staticmethod
    def go_to_menu(state, action):
        return extend(state, {'location': 'menu'})
    @staticmethod
    def set_books(state, action):
        width, height = dimensions(state)
        books = []
        for filename in action['value']:
            books.append(
                {
                    'data': BookFile_List(filename, [width, height]),
                    'page': 0
                }
            )
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        library = {'data': data, 'page': 0}
        return extend(state, {'books': tuple(books), 'library': library})
    @staticmethod
    def next_page(state, action):
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
    @staticmethod
    def previous_page(state, action):
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
    @staticmethod
    def replace_library(state, action):
        return state
    @staticmethod
    def shutdown(state, action):
        return state
    @staticmethod
    def backup_log(state, action):
        return state


action_types = utility.get_methods(Reducers)

def make_action_method(name):
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))

