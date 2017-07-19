from .. import utility
from ..book.reducers import BookReducers

print(dir(BookReducers()))

class GoToPageReducers():
    def go_to_page_enter_number(self, state, value):
        selection = state['go_to_page_selection']
        return state.copy(go_to_page_selection=selection + str(value))

    def go_to_page_confirm(self, state, value):
        selection = state['go_to_page_selection']
        if selection == '':
            return state
        page = int(selection)
        go_to_page = (BookReducers()).go_to_page
        return go_to_page(state.copy(go_to_page_selection=''), page)


    def go_to_page_delete(self, state, value):
        selection = state['go_to_page_selection']
        return state.copy(go_to_page_selection=selection[0:-1])
