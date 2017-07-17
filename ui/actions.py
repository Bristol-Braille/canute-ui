import logging
from frozendict import frozendict
from . import utility
from .library_reducers import LibraryReducers


log = logging.getLogger(__name__)


class AppReducers():
    def trigger(self, state, value):
        '''bit ugly but gives the abiliy to trigger any state subscribers'''
        return state

    def set_dimensions(self, state, value):
        dimensions = frozendict({'width': value[0], 'height': value[1]})
        return state.copy(dimensions=dimensions)

    def go_to_library(self, state, value):
        return state.copy(location='library')

    def go_to_menu(self, state, value):
        return state.copy(location='menu')

    def next_page(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page = state['library']['page'] + 1
            library = set_page(library, page, (height - 1))
            return state.copy(library=library)
        elif type(location) == int:
            book = state['books'][location]
            page = book['page'] + 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return state.copy(books=tuple(books))
        return state

    def previous_page(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page = library['page'] - 1
            library = set_page(library, page, (height - 1))
            return state.copy(library=library)
        elif type(location) == int:
            book = state['books'][location]
            page = book['page'] - 1
            books = list(state['books'])
            books[location] = set_page(book, page, height)
            return state.copy(books=tuple(books))
        return state

    def go_to_start(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        book = state['books'][location]
        page = 0
        books = list(state['books'])
        books[location] = set_page(book, page, height)
        return state.copy(books=tuple(books))

    def skip_pages(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        book = state['books'][location]
        page = book['page'] + value
        books = list(state['books'])
        books[location] = set_page(book, page, height)
        return state.copy(books=tuple(books))

    def replace_library(self, state, value):
        if state['replacing_library'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(replacing_library=value)

    def backup_log(self, state, value):
        if state['backing_up_log'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(backing_up_log=value)

    def update_ui(self, state, value):
        return state.copy(update_ui=value)

    def shutdown(self, state, value):
        return state.copy(shutting_down=True)


class HardwareReducers():
    def warm_up(self, state, value):
        if state['warming_up'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(warming_up=value)

    def reset_display(self, state, value):
        if state['resetting_display'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(resetting_display=value)


def set_page(book, page, height):
    data = book['data']
    if page < 0 or page > utility.get_max_pages(data, height):
        return book
    else:
        return frozendict({'data': data, 'page': page})


def make_action_method(name):
    '''Returns a method that returns a dict to be passed to dispatch'''
    def action_method(value=None):
        return {'type': name, 'value': value}
    return action_method


action_types = utility.get_methods(AppReducers)
action_types.extend(utility.get_methods(LibraryReducers))
action_types.extend(utility.get_methods(HardwareReducers))

# just an empty object


def actions(): pass


# then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))
