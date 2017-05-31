import os
import pydux
from frozendict import frozendict

import logging
log = logging.getLogger(__name__)

import utility
from functools import partial

class AppReducers():
    def trigger(self, state, value):
        '''bit ugly but gives the abiliy to trigger any state subscribers'''
        return state
    def set_dimensions(self, state, value):
        return state.copy(dimensions = frozendict({'width': value[0], 'height': value[1]}))
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
    def add_books(self, state, books_to_add):
        width, height = dimensions(state)
        book_filenames = map(lambda b: b['data'].filename, state['books'])
        books_to_add = filter(lambda d: d.filename not in book_filenames, books_to_add)
        books_to_add = map(lambda b: {'data': b, 'page':0}, books_to_add)
        books = list(state['books'])
        books += list(books_to_add)
        books = sort_books(books)
        data = map(get_title, books)
        data = map(partial(utility.pad_line, width), data)
        library = frozendict({'data': tuple(data), 'page': state['library']['page']})
        return state.copy(books = tuple(books), library = library)
    def remove_books(self, state, filenames):
        width, height = dimensions(state)
        books = filter(lambda b: b['data'].filename not in filenames, state['books'])
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
            return state.copy(books = tuple(books))
        return state
    def go_to_start(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        book = state['books'][location]
        page = 0
        books = list(state['books'])
        books[location] = set_page(book, page, height)
        return state.copy(books = tuple(books))
    def skip_pages(self, state, value):
        width, height = dimensions(state)
        location = state['location']
        book = state['books'][location]
        data = book['data']
        page = book['page'] + value
        books = list(state['books'])
        books[location] = set_page(book, page, height)
        return state.copy(books = tuple(books))
    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(replacing_library = value)
    def backup_log(self, state, value):
        if state['backing_up_log'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(backing_up_log = value)
    def update_ui(self, state, value):
        return state.copy(update_ui = value)
    def shutdown(self, state, value):
        return state.copy(shutting_down = True)


class HardwareReducers():
    def warm_up(self, state, value):
        if state['warming_up'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(warming_up = value)
    def reset_display(self, state, value):
        if state['resetting_display'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(resetting_display = value)



def sort_books(books):
    return sorted(books, key=lambda book: book['data'].filename)


def dimensions(state):
    width = state['dimensions']['width']
    height = state['dimensions']['height']
    return [width, height]


def get_title(book):
    basename = os.path.basename(book['data'].filename)
    title = os.path.splitext(basename)[0].replace('_', ' ')
    return utility.alphas_to_pin_nums(title)


def set_page(book, page, height):
    data = book['data']
    if page < 0 or page > get_max_pages(data, height):
        return book
    else:
        return frozendict({'data': data, 'page': page})


def get_max_pages(data, height):
    return (len(data) - 1) // height


def make_action_method(name):
    '''Returns a method that returns a dict to be passed to dispatch'''
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


action_types = utility.get_methods(AppReducers)
action_types.extend(utility.get_methods(HardwareReducers))

#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))

