class PageMenuReducers():
    def page_menu_enter_number(self, state, value):
        selection = state['selection']
        return state.copy(selection=selection + str(value))

    def page_menu_delete_last_entry(self, state, value):
        selection = state['selection']
        return state.copy(selection=selection[0:-1])
