import pickle
import aiofiles
import logging
from . import utility
from .system_menu.system_menu import menu_titles
from .manual import manual

STATE_FILE = 'state.pkl'

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


def read():
    log.debug('reading initial state from %s' % STATE_FILE)
    try:
        with open(STATE_FILE, 'rb') as fh:
            user_state = utility.freeze(pickle.load(fh))
    except:
        log.debug('error reading state file, using hard-coded initial state')
        user_state = initial_state['app']['user']
    return initial_state.copy(app=initial_state['app'].copy(user=user_state))


prev = {}


async def write(store):
    global prev
    state = store.state
    user_state = state['app']['user']
    write_state = utility.unfreeze(user_state)
    books = write_state['books']
    changed_books = []
    for book in books:
        # make sure deleted bookmarks are fully deleted
        bookmarks = tuple(bm for bm in book.bookmarks if bm != 'deleted')
        # also delete actual book data as it's too much for constantly saving
        book = book._replace(pages=None,
                             file_contents=None, bookmarks=bookmarks, loading=False)
        changed_books.append(book)
    write_state['books'] = changed_books
    if write_state != prev:
        log.debug('writing state file')
        prev = write_state
        pickle_data = pickle.dumps(write_state)
        async with aiofiles.open(STATE_FILE, 'wb') as fh:
            try:
                await fh.write(pickle_data)
            except:
                log.error('could not write state file {}')
