import pickle
import logging
from . import utility
from .system_menu.system_menu import menu_titles

STATE_FILE = 'state.pkl'

log = logging.getLogger(__name__)


initial_state = utility.freeze({
    'app': {
        'location': 'library',
        'library': {'data': [], 'page': 0},
        'book': 0,
        'books': [],
        'system_menu': {
            'data': [utility.pad_line(40, l) for l in menu_titles],
            'page': 0
        },
        'go_to_page': {
            'selection': '',
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
            state = pickle.load(fh)
            return state
    except:
        log.debug('error reading state file, using hard-coded initial state')
        return initial_state


def write(state):
    log.debug('writing state file')
    write_state = utility.unfreeze(state)
    write_state['app']['library'] = state['app']['library'].copy(page=0)
    location = state['app']['location']
    if location == 'system_menu':
        location = 'library'
    write_state['app']['location'] = location
    write_state['app']['backing_up_log'] = False
    write_state['app']['replacing_library'] = False
    write_state['hardware']['resetting_display'] = False
    write_state['hardware']['warming_up'] = False
    write_state['app']['shutting_down'] = False
    with open(STATE_FILE, 'wb') as fh:
        pickle.dump(utility.freeze(write_state), fh)
