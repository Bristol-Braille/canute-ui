from .book.state import UserState
from .library.state import LibraryState
from .go_to_page.state import GoToPageState
from .bookmarks.state import BookmarksState
from .language.state import LanguageState

from .book.help import render_book_help, render_home_menu_help
from .library.view import render_help as render_library_help
from .system_menu.help import render_help as render_system_help
from .language.view import render_help as render_language_help
from .go_to_page.view import render_help as render_gtp_help
from .bookmarks.help import render_help as render_bookmarks_help


class StateEvent(object):
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def __call__(self, *args, **kwargs):
        for handler in self.handlers:
            res = handler(*args, **kwargs)


class HelpState:
    def __init__(self, root):
        self.root = root

        self.visible = False
        self.page = 0

    def toggle(self):
        self.visible = not self.visible
        self.page = 0
        self.root.refresh_display()


class SystemMenuState:
    def __init__(self, root):
        self.page = 0


class AppState:
    def __init__(self, root: 'RootState'):
        self.root = root

        self.location = 'book'
        self.help_menu = HelpState(root)
        self.system_menu = SystemMenuState(root)
        self._width = 40
        self._height = 9
        self.home_menu_visible = False
        self.user = UserState(root)

        self.library = LibraryState(root)
        self.bookmarks_menu = BookmarksState(root)
        self.languages = LanguageState(root)
        self.go_to_page_menu = GoToPageState(root)

        self.loading_books = False
        self.replacing_library = False
        self.backing_up_log = False
        self.shutting_down = False

    @property
    def dimensions(self):
        return self._width, self._height

    @property
    def location_or_help_menu(self):
        return 'help_menu' if self.help_menu.visible else self.location

    def set_dimensions(self, value):
        self._width = value[0]
        self._height = value[1]

    def go_to_library(self):
        self.location = 'library'
        self.root.refresh_display()

    def go_to_system_menu(self):
        self.location = 'system_menu'
        self.root.refresh_display()

    def go_to_bookmarks_menu(self):
        self.location = 'bookmarks_menu'
        self.root.refresh_display()

    def go_to_language_menu(self):
        self.location = 'language'
        self.root.refresh_display()

    def close_menu(self, prune_bookmarks=False):
        # fully delete deleted bookmarks if required
        if prune_bookmarks:
            book = self.user.book
            bookmarks = book.bookmarks_pruned
            if bookmarks is not book.bookmarks:
                book = book._replace(bookmarks=bookmarks)
                self.user.books[self.user.current_book] = book
        self.location = 'book'
        self.bookmarks_menu.page = 0
        self.home_menu_visible = False
        self.go_to_page_menu.selection = ''
        self.help_menu.visible = False
        self.help_menu.page = 0
        self.root.refresh_display()

    def go_to_page(self, page):
        width, height = self.dimensions

        if page < 0:
            page = 0

        location = self.location_or_help_menu
        save_book = None

        if location == 'library':
            if page >= self.library.pages:
                page = self.library.pages - 1
            elif page < 0:
                page = 0
            self.library.page = page
        elif location == 'book':
            book_n = self.user.current_book
            book = self.user.books[book_n]
            book = book.set_page(page)
            # book files are frozen, so you have to replace
            self.user.books[book_n] = book
            save_book = book
        elif location == 'bookmarks_menu':
            book_n = self.user.current_book
            book = self.user.books[book_n]
            bookmarks_data = book.bookmarks
            # Account for title line.
            effective_height = height - 1
            num_pages = (len(bookmarks_data) +
                         (effective_height-1)) // effective_height
            if page >= num_pages - 1:
                page = num_pages - 1
            self.bookmarks_menu.page = page
        elif location == 'language':
            # TODO check if this is still used - replaced by select_language?
            lang_n = self.user.current_language  # default to 'en_GB:en' ?
            lang = list(self.languages.available.keys())[lang_n]
            self.user.current_language = lang
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
            if state.app.home_menu_visible:
                mapping['book'] = render_home_menu_help
            help_getter = mapping.get(self.location)
            num_pages = 1
            if help_getter:
                num_pages = len(help_getter(width, height)) // height
            if page >= num_pages:
                page = num_pages - 1
            self.help_menu.page = page

        self.root.refresh_display()

        if save_book is not None:
            self.root.save_state(save_book)

    def skip_pages(self, value):
        location = self.location_or_help_menu

        if location == 'library':
            self.go_to_page(self.library.page + value)
        elif location == 'book':
            page = self.user.book.page_number + value
            self.go_to_page(page)
        elif location == 'bookmarks_menu':
            self.go_to_page(self.bookmarks_menu.page + value)
        elif location == 'language':
            self.go_to_page(self.languages.page + value)
        elif location == 'help_menu':
            self.go_to_page(self.help_menu.page + value)

    def next_page(self):
        self.skip_pages(1)

    def previous_page(self):
        self.skip_pages(-1)

    def backup_log(self, value='start'):
        if self.backing_up_log != 'in progress' or value == 'done':
            self.backing_up_log = value

    def shutdown(self):
        self.shutting_down = True

    def load_books(self, value):
        # pretty certain this doesn't do anything
        self.loading_books = value


class HardwareState:
    def __init__(self, root):
        self.warming_up = False
        self.resetting_display = False

    def warm_up(self, value):
        if self.warming_up != 'in progress' or value == 'done':
            self.warming_up = value

    def reset_display(self, value='start'):
        if self.resetting_display != 'in progress' or value == 'done':
            self.resetting_display = value


class RootState:
    def __init__(self):
        self.app = AppState(self)
        self.hardware = HardwareState(self)

        self.refresh_display = StateEvent()
        self.save_state = StateEvent()
        self.backup_log = StateEvent()


state = RootState()
