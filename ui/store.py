import os
import pydux
from pydux.extend import extend
from pydux.create_store import create_store

from bookfile_list import BookFile_List
import utility

action_types = ['set_books', 'go_to_book', 'next_page', 'previous_page']

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
        }
    }
}

initial_state = {
    'location'        : 'library',
    'library'         : {'data': [], 'page': 0},
    'books'           : [],
    'button_bindings' : button_bindings,
    'display'         : {'width': 40, 'height': 9}
}


def get_max_pages(data, height):
    return len(data) // height


def get_title(book):
    return utility.alphas_to_pin_nums(os.path.basename(book['data'].filename))


def reducer(state, action = None):
    width = state['display']['width']
    height = state['display']['height']
    if action['type'] == 'go_to_book':
        try:
            location = state['books'][action['value']]
        except:
            log.warning('no book at {}'.format(action['value']))
            return state
        return extend(state, {'location': location})
    elif action['type'] == 'set_books':
        books = []
        for filename in action['value']:
            books.append(
                {
                    'data': BookFile_List(filename, [width, height]),
                    'page': 0
                }
            )
        library = {'data': map(get_title, books), 'page': 0}
        return extend(state, {'books': books, 'library': library})
    elif action['type'] == 'next_page':
        if state['location'] == 'library':
            data = state['library']['data']
            page = state['library']['page'] + 1
            if page > get_max_pages(data, height):
                return state
            else:
                return extend(state, {'library': {'data': data, 'page': page}})
    elif action['type'] == 'previous_page':
        if state['location'] == 'library':
            data = state['library']['data']
            page = state['library']['page'] - 1
            if page < 0:
                return state
            else:
                return extend(state, {'library': {'data': data, 'page': page}})
    return state


store = create_store(reducer, initial_state)
