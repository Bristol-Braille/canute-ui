from ..book.reducers import BookReducers
from .. import utility


class BookmarksReducers():
    def go_to_bookmark(self, state, n):
        width, height = utility.dimensions(state)
        page = state['bookmarks_menu']['page']
        book_n = state['book']
        book = state['books'][book_n]
        bookmarks = book.bookmarks[page * height:(page * height) + height]
        bookmark = bookmarks[n]
        set_book_page = BookReducers().set_book_page
        return set_book_page(state, bookmark)
