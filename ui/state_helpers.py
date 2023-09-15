"""
State helpers
=======

contains various utility methods for getting information on the state
"""
from .book.book_file import LoadState


def get_current_book(state):
    user = state['user']
    filename = user['current_book']
    return user['books'][filename]


def get_page_num_width(state):
    width, height = dimensions(state)
    book = get_current_book(state)
    max_pages = book.get_num_pages()
    return len(str(max_pages))


def dimensions(state):
    width = state['dimensions']['width']
    height = state['dimensions']['height']
    return (width, height)


def get_books(state):
    all_books = state['user']['books']
    successful_books = []
    for filename in all_books:
        book = all_books[filename]
        if book.load_state != LoadState.FAILED:
            successful_books.append(book)
    return tuple(successful_books)


def get_books_for_lib_page(state, page=None):
    width, height = dimensions(state)
    if page is None:
        page = state['library']['page']
    books = get_books(state)
    return books[page * height:(page * height) + height]
