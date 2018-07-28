from frozendict import FrozenOrderedDict
from collections import OrderedDict
from ..book.reducers import BookReducers
from .. import state_helpers


class BookmarksReducers():
    def delete_bookmark(self, state, n):
        width, height = state_helpers.dimensions(state)
        # adjust for title
        height -= 1
        page = state['bookmarks_menu']['page']
        book_n = state['user']['current_book']
        books = OrderedDict(state['user']['books'])
        book = books[book_n]
        bookmarks = book.bookmarks
        line = page * height
        # don't delete go-to-start end and go-to-end bookmarks
        if (line + n) == 0 or (line + n) == (len(bookmarks) - 1):
            return state
        changed_bookmarks = list(bookmarks[line:line + height])
        if n >= len(changed_bookmarks):
            return state
        changed_bookmarks[n] = 'deleted'
        bookmarks = bookmarks[0:line] + tuple(changed_bookmarks) \
            + bookmarks[line + height:len(bookmarks)]
        books[book_n] = book._replace(bookmarks=bookmarks)
        return state.copy(user=state['user'].copy(books=FrozenOrderedDict(books)))

    def go_to_bookmark(self, state, n):
        width, height = state_helpers.dimensions(state)
        # adjust for title
        height -= 1
        page = state['bookmarks_menu']['page']
        book_n = state['user']['current_book']
        book = state['user']['books'][book_n]
        bookmarks = book.bookmarks[page * height:(page * height) + height]
        if n >= len(bookmarks):
            return state
        bookmark = bookmarks[n]
        if bookmark == 'deleted':
            return state
        set_book_page = BookReducers().set_book_page
        return set_book_page(state, bookmark)
