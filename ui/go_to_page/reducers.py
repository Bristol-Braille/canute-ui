import re
from ..book.reducers import BookReducers
from .. import utility


class GoToPageReducers():
    def go_to_page_set_selection(self, state, _):
        go_to_page = state['go_to_page']
        selection = go_to_page['selection'] + go_to_page['keys_pressed']

        # handle delete ('<') characters
        r = re.compile('\d<')
        while r.search(selection) is not None:
            selection = r.sub('', selection)
        # any left over delete characters after numbers are ignored
        selection = ''.join([c for c in selection if c != '<'])

        # overwrite characters when exceeding max page num width
        num_width = utility.get_page_num_width(state)
        selection = selection[-num_width:]

        go_to_page = go_to_page.copy(selection=selection, keys_pressed='')
        return state.copy(go_to_page=go_to_page)

    def go_to_page_key_press(self, state, value):
        go_to_page = state['go_to_page']
        keys_pressed = go_to_page['keys_pressed'] + str(value)
        go_to_page = go_to_page.copy(keys_pressed=keys_pressed)
        return state.copy(go_to_page=go_to_page)

    def go_to_page_confirm(self, state, value):
        state = self.go_to_page_set_selection(state, None)
        go_to_page = state['go_to_page']
        selection = go_to_page['selection']
        if selection == '':
            return state
        go_to_page = go_to_page.copy(selection='')
        page = int(selection) - 1
        set_book_page = BookReducers().set_book_page
        return set_book_page(state.copy(go_to_page=go_to_page), page)

    def go_to_page_delete(self, state, value):
        go_to_page = state['go_to_page']
        selection = go_to_page['selection'][0:-1]
        return state.copy(go_to_page=go_to_page.copy(selection=selection))
