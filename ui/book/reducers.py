from .. import utility


class BookReducers():
    def go_to_start(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        book = state['books'][location]
        page = 0
        books = list(state['books'])
        books[location] = utility.set_page(book, page, height)
        return state.copy(books=tuple(books))

    def skip_pages(self, state, value):
        width, height = utility.dimensions(state)
        location = state['location']
        book = state['books'][location]
        page = book.page + value
        books = list(state['books'])
        books[location] = utility.set_page(book, page, height)
        return state.copy(books=tuple(books))

    def enter_go_to_page(self, state, value):
        return state.copy(home_menu_visible=False, location='go_to_page')

    def toggle_home_menu(self, state, value):
        return state.copy(home_menu_visible=not state['home_menu_visible'])
