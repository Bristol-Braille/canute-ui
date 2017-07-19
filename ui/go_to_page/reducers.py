class PageMenuReducers():
    def go_to_page_enter_number(self, state, value):
        selection = state['selection']
        return state.copy(selection=selection + str(value))

    def go_to_page_delete_last_entry(self, state, value):
        selection = state['selection']
        return state.copy(selection=selection[0:-1])
