import logging
from frozendict import frozendict, FrozenOrderedDict
from collections import OrderedDict
from . import utility
from . import state_helpers
from .library.reducers import LibraryReducers
from .book.reducers import BookReducers
from .go_to_page.reducers import GoToPageReducers
from .bookmarks.reducers import BookmarksReducers
from .language.reducers import LanguageReducers

from .book.help import render_book_help, render_home_menu_help
from .library.view import render_help as render_library_help
from .system_menu.help import render_help as render_system_help
from .language.view import render_help as render_language_help
from .go_to_page.view import render_help as render_gtp_help
from .bookmarks.help import render_help as render_bookmarks_help


log = logging.getLogger(__name__)


class AppReducers():
    def set_user_state(self, state, value):
        return state.copy(user=value)

    def trigger(self, state, value):
        '''bit ugly but gives the ability to trigger any state subscribers'''
        return state.copy()

    def set_dimensions(self, state, value):
        dimensions = frozendict(width=value[0], height=value[1])
        return state.copy(dimensions=dimensions)

    def go_to_library(self, state, _):
        return state.copy(location='library')

    def go_to_system_menu(self, state, _):
        return state.copy(location='system_menu')

    def go_to_bookmarks_menu(self, state, _):
        return state.copy(location='bookmarks_menu')

    def go_to_language_menu(self, state, _):
        return state.copy(location='language')

    def toggle_help_menu(self, state, _):
        visible = state['help_menu']['visible']
        help_menu = frozendict(visible=not visible, page=0)
        return state.copy(help_menu=help_menu)

    def close_menu(self, state, value):
        books = state['user']['books']
        # fully delete deleted bookmarks
        changed_books = OrderedDict()
        for filename in books:
            book = books[filename]
            bookmarks = tuple(bm for bm in book.bookmarks if bm != 'deleted')
            book = book._replace(bookmarks=bookmarks)
            changed_books[filename] = book
        bookmarks_menu = state['bookmarks_menu']
        return state.copy(location='book',
                          bookmarks_menu=bookmarks_menu.copy(page=0),
                          home_menu_visible=False, go_to_page_selection='',
                          help_menu=frozendict({'visible': False, 'page': 0}),
                          user=state['user'].copy(books=FrozenOrderedDict(changed_books)))

    def go_to_page(self, state, page):
        width, height = state_helpers.dimensions(state)

        if page < 0:
            page = 0

        if state['help_menu']['visible']:
            location = 'help_menu'
        else:
            location = state['location']

        if location == 'library':
            books = state['user']['books']
            max_pages = (len(books) - 1) // (height - 1)
            if page > max_pages:
                page = max_pages
            elif page < 0:
                page = 0
            library = frozendict({'page': page})
            return state.copy(library=library)
        elif location == 'book':
            book_n = state['user']['current_book']
            book = state['user']['books'][book_n]
            books = OrderedDict(state['user']['books'])
            book = book.set_page(page)
            books[book_n] = book
            return state.copy(user=state['user'].copy(books=FrozenOrderedDict(books)))
        elif location == 'bookmarks_menu':
            book_n = state['user']['current_book']
            book = state['user']['books'][book_n]
            bookmarks_data = book.bookmarks
            max_pages = (len(bookmarks_data) - 1) // height
            if page > max_pages:
                page = max_pages
            bookmarks_menu = state['bookmarks_menu'].copy(page=page)
            return state.copy(bookmarks_menu=bookmarks_menu)
        elif location == 'language':
            lang_n = state['user'].get('current_language', 'en_GB:en')
            lang = list(state['languages']['available'].keys())[lang_n]
            language_menu = state['user'].copy(current_language=lang)
            return state.copy(language=language_menu)
        elif location == 'help_menu':

            # To calculate help page bounds and ensure we stay within
            # them, do a dummy render of the help and count the pages.

            mapping = {
                'book': render_book_help,
                'library': render_library_help,
                'system_menu': render_system_help,
                'language': render_language_help,
                'bookmarks_menu': render_bookmarks_help,
                'go_to_page': render_gtp_help,
            }
            if state['home_menu_visible']:
                mapping['book'] = render_home_menu_help
            help_getter = mapping.get(state['location'])
            num_pages = 1
            if help_getter:
                num_pages = len(help_getter(width, height)) // height
            if page >= num_pages:
                page = num_pages - 1
            return state.copy(help_menu=state['help_menu'].copy(page=page))
        return state

    def skip_pages(self, state, value):
        if state['help_menu']['visible']:
            location = 'help_menu'
        else:
            location = state['location']

        if location == 'library':
            page = state['library']['page'] + value
            return self.go_to_page(state, page)
        elif location == 'book':
            book_n = state['user']['current_book']
            page = state['user']['books'][book_n].page_number + value
            return self.go_to_page(state, page)
        elif location == 'bookmarks_menu':
            page = state['bookmarks_menu']['page'] + value
            return self.go_to_page(state, page)
        elif location == 'language_menu':
            page = state['language_menu']['page'] + value
            return self.go_to_page(state, page)
        elif location == 'help_menu':
            page = state['help_menu']['page'] + value
            return self.go_to_page(state, page)
        return state

    def next_page(self, state, _):
        return self.skip_pages(state, 1)

    def previous_page(self, state, _):
        return self.skip_pages(state, -1)

    def backup_log(self, state, value):
        if state['backing_up_log'] == 'in progress' and value != 'done':
            return state
        else:
            return state.copy(backing_up_log=value)

    def shutdown(self, state, value):
        return state.copy(shutting_down=True)

    def load_books(self, state, value):
        return state.copy(load_books=value)

    def do_nothing(self, state, value):
        return state


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
action_types.extend(utility.get_methods(LanguageReducers))
action_types.extend(utility.get_methods(LibraryReducers))
action_types.extend(utility.get_methods(BookReducers))
action_types.extend(utility.get_methods(GoToPageReducers))
action_types.extend(utility.get_methods(HardwareReducers))
action_types.extend(utility.get_methods(BookmarksReducers))


def actions():
    '''just an empty object'''
    pass


# then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))
