from functools import partial
from pydux.extend import extend
import pickle
import logging
log = logging.getLogger(__name__)

import utility
import menu


initial_state = {
    'location'        : 'library',
    'library'         : {'data': tuple(), 'page': 0},
    'menu'            : {
        'data': map(partial(utility.pad_line, 40), menu.menu_titles_braille),
        'page': 0
    },
    'books'             : tuple(),
    'replacing_library' : False,
    'backing_up_log'    : False,
    'shutting_down'     : False,
    'display'           : {'width': 40, 'height': 9}
}

state_file = 'state.pkl'

def read():
    try:
        with open(state_file) as fh:
            return pickle.load(fh)
    except:
        log.debug('error reading state file, using hard-coded initial state')
        return initial_state


def write(state):
    log.debug('writing state file')
    #only select the bits of the state we wan't to persist
    state = extend(initial_state, {'books': state['books']})
    with open(state_file, 'w') as fh:
        pickle.dump(state, fh)
