import os
import pydux
from pydux.extend import extend
from pydux.create_store import create_store

import logging
log = logging.getLogger(__name__)

from bookfile_list import BookFile_List
import utility

HEIGHT = 9

initial_state = {
    'location'        : {'item': 'library', 'page': 0},
    'books'           : [],
    'button_bindings' : {}
}

def update(state = initial_state, action = None):
    if action['type'] == 'GO_TO_BOOK':
        try:
            location = state['books'][action['value']]
        except IndexError:
            log.warning('no book at {}'.format(action['value']))
            return state
        return extend(
            state,
            {'location': location}
        )
    return state

store = create_store(update)

def render(state):
    if state['location']['item'] == 'library':
        render_library(state.page, state.books)

def get_title(book):
    return map(utility.alphas_to_pin_nums, os.path.basename(book.filename))

def render_library(page, books):
    n = page * HEIGHT
    lines = map(get_title, books)[n : n + HEIGHT]
    driver.set_braille(lines)

def render_book(page, book):
    n = page * HEIGHT
    lines = book[n : n + HEIGHT]
    driver.set_braille(lines)
