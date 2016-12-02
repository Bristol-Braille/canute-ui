import os
import pydux
from pydux.extend import extend
from pydux.create_store import create_store
from functools import partial

import logging
log = logging.getLogger(__name__)

from bookfile_list import BookFile_List
import utility

action_types = ['set_books', 'go_to_book', 'go_to_library', 'next_page', 'previous_page']


def make_action_method(name):
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))


button_bindings = {
    'library': {
        'single': {
            '>' : actions.next_page,
            '<' : actions.previous_page,
            '1' : partial(actions.go_to_book, 0),
            '2' : partial(actions.go_to_book, 1),
            '3' : partial(actions.go_to_book, 2),
            '4' : partial(actions.go_to_book, 3),
            '5' : partial(actions.go_to_book, 4),
            '6' : partial(actions.go_to_book, 5),
            '7' : partial(actions.go_to_book, 6),
            '8' : partial(actions.go_to_book, 7),
            '9' : partial(actions.go_to_book, 8),
        }
    },
    'book': {
        'single': {
            '>' : actions.next_page,
            '<' : actions.previous_page,
            'L' : actions.go_to_library
        }
    }
}

initial_state = {
    'location'        : 'library',
    'library'         : {'data': [], 'page': 0},
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
