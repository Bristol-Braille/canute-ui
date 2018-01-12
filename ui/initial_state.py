import logging
from collections import OrderedDict
import toml
import os
from frozendict import frozendict
from . import utility
from .system_menu.system_menu import menu_titles
from .manual import manual
from .book_file import BookFile

STATE_FILE = 'state.pkl'
USER_STATE_FILE = '.canute_state.toml'

log = logging.getLogger(__name__)


initial_state = utility.freeze({
    'app': {
        'user': {
            'book': 0,
            'books': [manual],
        },
        'location': 'book',
        'library': {
            'page': 0,
        },
        'load_books': False,
        'system_menu': {
            'data': [utility.pad_line(40, l) for l in menu_titles],
            'page': 0
        },
        'bookmarks_menu': {
            'page': 0
        },
        'go_to_page': {
            'selection': '',
            'keys_pressed': '',
        },
        'help_menu': {
            'visible': False,
            'page': 0,
        },
        'replacing_library': False,
        'backing_up_log': False,
        'update_ui': False,
        'shutting_down': False,
        'dimensions': {'width': 40, 'height': 9},
        'home_menu_visible': False,
    },
    'hardware': {
        'warming_up': False,
        'resetting_display': False,
    },
})

prev = initial_state['app']['user']


def to_state_file(book_path):
    basename = os.path.basename(book_path)
    dirname = os.path.dirname(book_path)
    return os.path.join(dirname, '.canute.' + basename + '.toml')


def read_user_state(path):
    global prev
    book_files = utility.find_files(path, ('brf', 'pef'))
    main_toml = os.path.join(path, USER_STATE_FILE)
    book_number = 0
    if os.path.exists(main_toml):
        main_state = toml.load(main_toml)
        if 'current_book' in main_state:
            book_number = main_state['current_book']
    books = []
    for book_file in book_files:
        toml_file = to_state_file(book_file)
        book = BookFile(filename=book_file, width=40, height=9)
        if os.path.exists(toml_file):
            t = toml.load(toml_file)
            if 'current_page' in t:
                book = book._replace(page_number=t['current_page'])
            if 'bookmarks' in t:
                book = book._replace(bookmarks=tuple(t['bookmarks']))
        books.append(book)
    user_state = frozendict(books=books, book=book_number)
    prev = user_state
    return user_state


def read(path):
    user_state = read_user_state(path)
    return initial_state.copy(app=initial_state['app'].copy(user=user_state))


async def write(store, library_dir):
    global prev
    state = store.state
    user_state = state['app']['user']
    books = user_state['books']
    selected_book = user_state['book']
    if selected_book != prev['book']:
        with open(os.path.join(library_dir, USER_STATE_FILE), 'w') as f:
            toml.dump({'current_book': selected_book}, f)
    for i, book in enumerate(books):
        prev_book = prev['books'][i]
        if book.page_number != prev_book.page_number or book.bookmarks != prev_book.bookmarks:
            path = to_state_file(book.filename)
            with open(path, 'w') as f:
                d = OrderedDict([['current_page', book.page_number],
                                 ['bookmarks', list(book.bookmarks)]])
                toml.dump(d, f)
    prev = user_state
