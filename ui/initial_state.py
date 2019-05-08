import logging
import aiofiles
from collections import OrderedDict
from frozendict import FrozenOrderedDict
import toml
import os
from frozendict import frozendict
from . import utility
from .manual import Manual, manual_filename
from .cleaning_and_testing import CleaningAndTesting, cleaning_filename
from .book.book_file import BookFile
from .i18n import install, DEFAULT_LOCALE, BUILTIN_LANGUAGES, OLD_DEFAULT_LOCALE
from . import config_loader

STATE_FILE = 'state.pkl'
USER_STATE_FILE = 'canute_state.txt'

manual = Manual.create()

log = logging.getLogger(__name__)

initial_state = utility.freeze({
    'app': {
        'user': {
            'current_book': manual_filename,
            'books': OrderedDict({manual_filename: manual}),
            'current_language': DEFAULT_LOCALE.code,
        },
        'location': 'book',
        'library': {
            'page': 0,
        },
        'load_books': False,
        'system_menu': {
            'page': 0
        },
        'bookmarks_menu': {
            'page': 0
        },
        'languages': {
            'available': BUILTIN_LANGUAGES,
            'selection': '',
            'keys_pressed': '',
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
    return os.path.join(dirname, 'canute.' + basename + '.txt')


async def read_user_state(path):
    global prev
    global manual
    current_book = manual_filename
    current_language = None
    book_files = utility.find_files(path, ('brf', 'pef'))
    config = config_loader.load()
    state_sources = ['sd_card_dir']
    if config.has_option('files', 'additional_lib_1'):
        state_sources.append('additional_lib_1')
    if config.has_option('files', 'additional_lib_2'):
        state_sources.append('additional_lib_2')
    for state_source in state_sources:
        _dir = config.get('files', state_source)
        main_toml = os.path.join(path, _dir, USER_STATE_FILE)
        if os.path.exists(main_toml):
            main_state = toml.load(main_toml)
            if 'current_book' in main_state:
                current_book = main_state['current_book']
                if not current_book == manual_filename:
                    current_book = os.path.join(path, current_book)
            if 'current_language' in main_state:
                current_language = main_state['current_language']
            break

    if not current_language or current_language == OLD_DEFAULT_LOCALE:
        current_language = DEFAULT_LOCALE.code

    install(current_language)
    manual = Manual.create()

    manual_toml = os.path.join(path, to_state_file(manual_filename))
    if os.path.exists(manual_toml):
        t = toml.load(manual_toml)
        if 'current_page' in t:
            manual = manual._replace(page_number=t['current_page'] - 1)
        if 'bookmarks' in t:
            manual = manual._replace(bookmarks=tuple(sorted(manual.bookmarks + tuple(
                bm - 1 for bm in t['bookmarks']))))

    books = OrderedDict({manual_filename: manual})
    for book_file in book_files:
        toml_file = to_state_file(book_file)
        book = BookFile(filename=book_file, width=40, height=9)
        if os.path.exists(toml_file):
            t = toml.load(toml_file)
            if 'current_page' in t:
                book = book._replace(page_number=t['current_page'] - 1)
            if 'bookmarks' in t:
                book = book._replace(bookmarks=tuple(sorted(book.bookmarks + tuple(
                    bm - 1 for bm in t['bookmarks']))))
        books[book_file] = book
    books[cleaning_filename] = CleaningAndTesting.create()

    if current_book not in books:
        current_book = manual_filename

    user_state = frozendict(books=FrozenOrderedDict(
        books), current_book=current_book, current_language=current_language)
    prev = user_state
    return user_state.copy(books=user_state['books'])


async def read(path):
    user_state = await read_user_state(path)
    return initial_state.copy(app=initial_state['app'].copy(user=user_state))


async def write(store, media_dir):
    global prev
    state = store.state
    user_state = state['app']['user']
    books = user_state['books']
    selected_book = user_state['current_book']
    selected_lang = user_state['current_language']
    if selected_book != prev['current_book']:
        if not selected_book == manual_filename:
            selected_book = os.path.relpath(selected_book, media_dir)
        s = toml.dumps({'current_book': selected_book,
                        'current_language': selected_lang})
        config = config_loader.load()
        sd_card_dir = config.get('files', 'sd_card_dir')
        path = os.path.join(media_dir, sd_card_dir, USER_STATE_FILE)
        async with aiofiles.open(path, 'w') as f:
            await f.write(s)
    for filename in books:
        book = books[filename]
        if filename in prev['books']:
            prev_book = prev['books'][filename]
        else:
            prev_book = BookFile()
        if book.page_number != prev_book.page_number or book.bookmarks != prev_book.bookmarks:
            path = to_state_file(book.filename)
            if book.filename == manual_filename:
                path = os.path.join(media_dir, path)
            bms = [bm + 1 for bm in book.bookmarks if bm != 'deleted']
            # remove start-of-book and end-of-book bookmarks
            bms = bms[1:-1]
            # ordered to make sure current_page comes before bookmarks
            d = OrderedDict([['current_page', book.page_number + 1],
                             ['bookmarks', bms]])
            s = toml.dumps(d)
            async with aiofiles.open(path, 'w') as f:
                await f.write(s)
    prev = user_state
