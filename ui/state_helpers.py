'''
State helpers
=======

contains various utility methods for getting information on the state
'''
from .book.book_file import LoadState


def get_page_num_width(state):
    width, height = dimensions(state)
    book = state['user']['books'][state['user']['current_book']]
    max_pages = len(book.pages)
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
