from ..book.reducers import BookReducers

class GoToPageReducers():
    def go_to_page_enter_number(self, state, value):
        go_to_page = state['go_to_page']
        selection = go_to_page['selection'] + str(value)
        if len(selection) > 3:
            return state
        if selection == '0':
            return state
        return state.copy(go_to_page=go_to_page.copy(selection=selection))

    def go_to_page_confirm(self, state, value):
        go_to_page = state['go_to_page']
        selection = go_to_page['selection']
        if selection == '':
            return state
        go_to_page = go_to_page.copy(selection='')
        page = int(selection) - 1
        go_to_page_reducer = (BookReducers()).go_to_page
        return go_to_page_reducer(state.copy(go_to_page=go_to_page), page)

    def go_to_page_delete(self, state, value):
        go_to_page = state['go_to_page']
        selection = go_to_page['selection'][0:-1]
        return state.copy(go_to_page=go_to_page.copy(selection=selection))
