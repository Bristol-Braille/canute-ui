import os
import pydux
from pydux.extend import extend

import logging
log = logging.getLogger(__name__)

import menu
from bookfile_list import BookFile_List
import utility
from actions import Reducers
import initial_state

reducers = Reducers()
reducer_dict = {}
for name in dir(reducers):
    if not name.startswith('__'):
        reducer_dict[name] = getattr(reducers, name)

def reducer(state, action = None):
    log.debug(action)
    for name in reducer_dict:
        if action['type'] == name:
            return reducer_dict[name](state, action['value'])
    return state

store = pydux.create_store(reducer)
