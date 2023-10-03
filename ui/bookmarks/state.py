from .. import state


class BookmarksState:
    def __init__(self, root: 'state.RootState'):
        self.root = root
        self.page = 0

    def delete_bookmark(self, state, n):
        width, height = self.root.app.dimensions
        # adjust for title
        height -= 1
        page = self.page
        book = self.root.app.user.book
        bookmarks = book.bookmarks
        line = page * height
        # don't delete go-to-start end and go-to-end bookmarks
        if (line + n) == 0 or (line + n) == (len(bookmarks) - 1):
            return state
        changed_bookmarks = list(bookmarks[line:line + height])
        if n >= len(changed_bookmarks):
            return
        changed_bookmarks[n] = 'deleted'
        bookmarks = bookmarks[0:line] + tuple(changed_bookmarks) \
            + bookmarks[line + height:len(bookmarks)]
        book = book._replace(bookmarks=bookmarks)
        self.root.app.user.books[self.root.app.user.current_book] = book

    def go_to_bookmark(self, n):
        width, height = self.root.app.dimensions
        # adjust for title
        height -= 1
        page = self.page
        book = self.root.app.user.book
        bookmarks = book.bookmarks[page * height:(page * height) + height]
        if n >= len(bookmarks):
            return
        bookmark = bookmarks[n]
        if bookmark == 'deleted':
            return
        self.root.app.user.set_book_page(bookmark)
