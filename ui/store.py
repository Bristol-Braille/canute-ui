import os
import pydux
from pydux.extend import extend
from pydux.create_store import create_store
from functools import partial

import logging
log = logging.getLogger(__name__)

import menu
from bookfile_list import BookFile_List
import utility
from actions import actions
from button_bindings import button_bindings

initial_state = {
    'location'        : 'library',
    'library'         : {'data': tuple(), 'page': 0},
    'menu'            : {
        'data': map(partial(utility.pad_line, 40), menu.menu_titles_braille),
        'page': 0
    },
    'books'           : tuple(),
    'button_bindings' : button_bindings,
    'display'         : {'width': 40, 'height': 9}
}


def get_max_pages(data, height):
    return len(data) // height


def get_title(book):
    return utility.alphas_to_pin_nums(os.path.basename(book['data'].filename))

def set_page(book, page, height):
    data = book['data']
    if page < 0 or page > get_max_pages(data, height):
        return book
    else:
        return {'data': data, 'page': page}


def reducer(state, action = None):
    width = state['display']['width']
    height = state['display']['height']
    location = state['location']
    if action['type'] == 'go_to_book':
        page = state['library']['page']
        line_number = page * height
        print(line_number)
        try:
            location = state['books'][line_number + action['value']]
        except:
            log.warning('no book at {}'.format(action['value']))
            return state
        return extend(state, {'location': line_number + action['value']})
    elif action['type'] == 'go_to_library':
        return extend(state, {'location': 'library'})
    elif action['type'] == 'go_to_menu':
        return extend(state, {'location': 'menu'})
    elif action['type'] == 'set_books':
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
    elif action['type'] == 'next_page':
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
    elif action['type'] == 'previous_page':
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


store = create_store(reducer, initial_state)
