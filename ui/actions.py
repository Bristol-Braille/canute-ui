import logging
from frozendict import frozendict
from . import utility
from .library.reducers import LibraryReducers
from .book.reducers import BookReducers
from .go_to_page.reducers import GoToPageReducers
from .bookmarks.reducers import BookmarksReducers


log = logging.getLogger(__name__)


class AppReducers():
    def trigger(self, state, value):
        '''bit ugly but gives the ability to trigger any state subscribers'''
        return state.copy()

    def set_dimensions(self, state, value):
        dimensions = frozendict({'width': value[0], 'height': value[1]})
        return state.copy(dimensions=dimensions)

    def go_to_library(self, state, value):
        return state.copy(location='library')

    def go_to_system_menu(self, state, value):
        return state.copy(location='system_menu')

    def go_to_bookmarks_menu(self, state, value):
        return state.copy(location='bookmarks_menu')

    def close_menu(self, state, value):
        return state.copy(location='book',
                          home_menu_visible=False, go_to_page_selection='')

    def go_to_page(self, state, page):
        width, height = utility.dimensions(state)
        location = state['location']
        if location == 'library':
            library = state['library']
            page = utility.set_page(library['data'], page, height - 1)
            library = frozendict({'data': library['data'], 'page': page})
            return state.copy(library=library)
        elif location == 'book':
            book_n = state['book']
            book = state['books'][book_n]
            books = list(state['books'])
            book.page = utility.set_page(book, page, height)
            books[book_n] = book
            return state.copy(books=tuple(books))
        elif location == 'bookmarks_menu':
            book_n = state['book']
            book = state['books'][book_n]
            bookmarks_data = book.bookmarks
            max_pages = utility.get_max_pages(bookmarks_data, height)
            if page < 0:
                page = 0
            elif page > max_pages:
                page = max_pages
            bookmarks_menu = state['bookmarks_menu'].copy(page=page)
            return state.copy(bookmarks_menu=bookmarks_menu)
        return state

    def next_page(self, state, _):
        location = state['location']
        if location == 'library':
            page = state['library']['page'] + 1
            return self.go_to_page(state, page)
        elif location == 'book':
            book_n = state['book']
            page = state['books'][book_n].page + 1
            return self.go_to_page(state, page)
        elif location == 'bookmarks_menu':
            page = state['bookmarks_menu']['page'] + 1
            return self.go_to_page(state, page)
        return state

    def previous_page(self, state, _):
        location = state['location']
        if location == 'library':
            page = state['library']['page'] - 1
            return self.go_to_page(state, page)
        elif location == 'book':
            book_n = state['book']
            page = state['books'][book_n].page - 1
            return self.go_to_page(state, page)
        elif location == 'bookmarks_menu':
            page = state['bookmarks_menu']['page'] - 1
            return self.go_to_page(state, page)
        return state

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


def make_action_method(name):
    '''Returns a method that returns a dict to be passed to dispatch'''
    def action_method(value=None):
        return {'type': name, 'value': value}
    return action_method


action_types = utility.get_methods(AppReducers)
action_types.extend(utility.get_methods(LibraryReducers))
action_types.extend(utility.get_methods(BookReducers))
action_types.extend(utility.get_methods(GoToPageReducers))
action_types.extend(utility.get_methods(HardwareReducers))
action_types.extend(utility.get_methods(BookmarksReducers))

# just an empty object


def actions(): pass


# then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))
