import logging
import aiofiles
from collections import OrderedDict
from frozendict import FrozenOrderedDict
import toml
import os
from frozendict import frozendict
from . import utility
from .manual import Manual, manual_filename
from .book.book_file import BookFile
from .book.handlers import init

STATE_FILE = 'state.pkl'
USER_STATE_FILE = 'canute_state.txt'
DEFAULT_LOCALE = 'en_GB:en'

manual = Manual.create(DEFAULT_LOCALE)

log = logging.getLogger(__name__)

initial_state = utility.freeze({
    'app': {
        'user': {
            'current_book': manual_filename,
            'books': OrderedDict({manual_filename: manual}),
            'current_language': DEFAULT_LOCALE
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
            'available': OrderedDict({
                'en_GB:en': 'English',
                'de_DE:de': 'German',
                'es_MX:es': 'Spanish (Mexican)'
            }),
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
    book_files = utility.find_files(path, ('brf', 'pef'))
    main_toml = os.path.join(path, 'sd-card', USER_STATE_FILE)
    current_book = manual_filename
    if os.path.exists(main_toml):
        main_state = toml.load(main_toml)
        if 'current_book' in main_state:
            current_book = main_state['current_book']
            if not current_book == manual_filename:
                current_book = os.path.join(path, current_book)
        if 'current_language' in main_state:
            current_language = main_state['current_language']
        else:
            current_language = 'en_GB:en'
    else:
        current_language = 'en_GB:en'

    manual_toml = os.path.join(path, to_state_file(manual_filename))
    if os.path.exists(manual_toml):
        t = toml.load(manual_toml)
        if 'current_page' in t:
            manual = manual._replace(page_number=t['current_page'] - 1)
        if 'bookmarks' in t:
            manual = manual._replace(bookmarks=tuple(sorted(manual.bookmarks + tuple(
                bm - 1 for bm in t['bookmarks']))))
    else:
        manual = Manual.create(current_language)

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
        try:
            books[book_file] = await init(book)
        except Exception as e:
            log.warning('could not open {}'.format(book_file))
            log.warning(e)

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
        path = os.path.join(media_dir, 'sd-card', USER_STATE_FILE)
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
