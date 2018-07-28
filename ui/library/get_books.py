from ..book.book_file import LoadState


def get_books(state):
    all_books = state['user']['books']
    successful_books = []
    for filename in all_books:
        book = all_books[filename]
        if book.load_state != LoadState.FAILED:
            successful_books.append(book)
    return tuple(successful_books)
