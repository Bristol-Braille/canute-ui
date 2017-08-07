from .. import utility


class BookReducers():
    def go_to_start(self, state, value):
        return self.set_book_page(state, 0)

    def go_to_end(self, state, value):
        width, height = utility.dimensions(state)
        book_n = state['book']
        book = state['books'][book_n]
        last_page = utility.get_max_pages(book, height)
        return self.set_book_page(state, last_page)

    def skip_pages(self, state, value):
        book_n = state['book']
        book = state['books'][book_n]
        page = book.page + value
        return self.go_to_page(state, page)

    def set_book_page(self, state, page):
        width, height = utility.dimensions(state)
        book_n = state['book']
        book = state['books'][book_n]
        books = list(state['books'])
        books[book_n].page = utility.set_page(book, page, height)
        return state.copy(books=tuple(books),
                          location='book', home_menu_visible=False)

    def enter_go_to_page(self, state, value):
        return state.copy(home_menu_visible=False, location='go_to_page')

    def toggle_home_menu(self, state, value):
        return state.copy(home_menu_visible=not state['home_menu_visible'])

    def insert_bookmark(self, state, _):
        number = state['book']
        books = list(state['books'])
        book = books[number]
        page = book.page
        if page not in book.bookmarks:
            book.bookmarks += tuple([page])
            books[number] = book
            return state.copy(books=tuple(books))
        return state
