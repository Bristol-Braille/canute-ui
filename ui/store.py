import aioredux
import logging
from .actions import AppReducers, HardwareReducers
from .library.reducers import LibraryReducers
from .book.reducers import BookReducers
from .go_to_page.reducers import GoToPageReducers
from .initial_state import initial_state


log = logging.getLogger(__name__)


def dictify(cls):
    reducers = cls()
    reducer_dict = {}
    for name in dir(reducers):
        if not name.startswith('__'):
            reducer_dict[name] = getattr(reducers, name)
    return reducer_dict


def makeReducer(key, clss):
    reducer_dict = {}

    for cls in clss:
        reducer_dict.update(dictify(cls))

    def reducer(state, action=None):
        if state is None:
            state = initial_state[key]
        for name in reducer_dict:
            if action['type'] == name:
                return reducer_dict[name](state, action['value'])
        return state
    return reducer


combined = aioredux.combine_reducers({
    'app': makeReducer('app', [AppReducers, LibraryReducers,
                               BookReducers, GoToPageReducers]),
    'hardware': makeReducer('hardware', [HardwareReducers]),
})


def main_reducer(state, action):
    if 'value' in action:
        log.debug('dispatching {}:{}'.format(action['type'], action['value']))
    else:
        log.debug('dispatching {}'.format(action['type']))
    if action['type'] == '@@redux/INIT':
        return initial_state
    if action['type'] == 'init':
        return action['value']
    if state is None:
        state = initial_state
    return combined(state, action)


