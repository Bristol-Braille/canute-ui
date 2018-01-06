from copy import copy
from ..book.reducers import BookReducers
from .. import utility


class BookmarksReducers():
    def delete_bookmark(self, state, n):
        width, height = utility.dimensions(state)
        # adjust for title
        height -= 1
        page = state['bookmarks_menu']['page']
        book_n = state['user']['book']
        books = list(state['user']['books'])
        book = copy(books[book_n])
        bookmarks = book.bookmarks
        line = page * height
        changed_bookmarks = list(bookmarks[line:line + height])
        if n >= len(changed_bookmarks):
            return state
        changed_bookmarks[n] = 'deleted'
        book.bookmarks = bookmarks[0:line]
        book.bookmarks += tuple(changed_bookmarks)
        book.bookmarks += bookmarks[line + height: len(bookmarks)]
        books[book_n] = book
        return state.copy(user=state['user'].copy(books=tuple(books)))

    def go_to_bookmark(self, state, n):
        width, height = utility.dimensions(state)
        # adjust for title
        height -= 1
        page = state['bookmarks_menu']['page']
        book_n = state['user']['book']
        book = state['user']['books'][book_n]
        bookmarks = book.bookmarks[page * height:(page * height) + height]
        if n >= len(bookmarks):
            return state
        bookmark = bookmarks[n]
        if bookmark == 'deleted':
            return state
        set_book_page = BookReducers().set_book_page
        return set_book_page(state, bookmark)
