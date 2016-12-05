import os
import pydux
from pydux.extend import extend
from functools import partial

import logging
log = logging.getLogger(__name__)

import menu
from bookfile_list import BookFile_List
import utility
from actions import Reducers
from initial_state import initial_state

reducer_dict = {}
for name in Reducers.__dict__:
    if not name.startswith('__'):
        reducer_dict[name] = getattr(Reducers.__dict__[name], '__func__')

def reducer(state, action = None):
    if state is None:
        state = initial_state
    for name in reducer_dict:
        if action['type'] == name:
            return reducer_dict[name](state, action)

store = pydux.create_store(reducer, initial_state)
