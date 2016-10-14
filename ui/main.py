import os

from bookfile_list import BookFile_List
import utility

HEIGHT = 9

initial_state = {
    'location'        : {'item': 'library', 'page': 0},
    'books'           : [],
    'button_bindings' : {}
}

def render(state):
    if (state['location']['item'] == 'library'):
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
