from functools import partial
from pydux.extend import extend
import pickle
import logging
log = logging.getLogger(__name__)

import utility
import menu


initial_state = {
    'location' : 'library',
    'library'  : {'data': tuple(), 'page': 0},
    'menu'     : {
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
    log.debug('reading initial state')
    try:
        with open(state_file) as fh:
            state = pickle.load(fh)
            return state
    except:
        log.debug('error reading state file, using hard-coded initial state')
        return extend(initial_state)


def write(state):
    log.debug('writing state file')
    #only select the bits of the state we want to persist
    state = extend(state, {'library': extend(state['library'], {'page': 0})})
    state['location']          = 'library'
    state['backing_up_log']    = False
    state['replacing_library'] = False
    state['shutting_down']     = False
    with open(state_file, 'w') as fh:
        pickle.dump(state, fh)
