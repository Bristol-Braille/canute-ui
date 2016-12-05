import os
import pydux
from pydux.extend import extend
from pydux.create_store import create_store
from functools import partial

import logging
log = logging.getLogger(__name__)

import menu
from bookfile_list import BookFile_List
import utility
from actions import Reducers
from button_bindings import button_bindings

initial_state = {
    'location'        : 'library',
    'library'         : {'data': tuple(), 'page': 0},
    'menu'            : {
        'data': map(partial(utility.pad_line, 40), menu.menu_titles_braille),
        'page': 0
    },
    'books'           : tuple(),
    'button_bindings' : button_bindings,
    'display'         : {'width': 40, 'height': 9}
}

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

store = create_store(reducer, initial_state)
