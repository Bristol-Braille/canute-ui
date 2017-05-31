import os
import pydux

import logging
log = logging.getLogger(__name__)

import menu
from bookfile_list import BookFile_List
import utility
from actions import Reducers
import initial_state

def dictify(cls):
    reducers = cls()
    reducer_dict = {}
    for name in dir(reducers):
        if not name.startswith('__'):
            reducer_dict[name] = getattr(reducers, name)
    return reducer_dict


def makeReducer(cls):
    reducer_dict = dictify(cls)
    def reducer(state, action = None):
        log.debug(action)
        for name in reducer_dict:
            if action['type'] == name:
                return reducer_dict[name](state, action['value'])
        return state
    return reducer

reducer = makeReducer(Reducers)

store = pydux.create_store(reducer)
