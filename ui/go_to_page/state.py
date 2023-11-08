import re
from .. import state


class GoToPageState:
    def __init__(self, root: 'state.RootState'):
        self.root = root
        self.selection = ''
        self.keys_pressed = ''

    def go_to_page_set_selection(self, refresh=True):
        selection = self.selection + self.keys_pressed

        # handle delete ('<') characters
        r = re.compile(r'\d<')
        if r.search(selection) is not None:
            selection = ''
        # any left over delete characters after numbers are ignored
        selection = ''.join([c for c in selection if c != '<'])

        # overwrite characters when exceeding max page num width
        num_width = self.root.app.user.book.page_num_width
        selection = selection[-num_width:]

        self.selection = selection
        self.keys_pressed = ''
        if refresh:
            self.root.refresh_display()

    def go_to_page_key_press(self, value):
        self.keys_pressed += str(value)

    def go_to_page_confirm(self):
        self.go_to_page_set_selection(False)
        if self.selection == '':
            return
        page = int(self.selection) - 1
        self.selection = ''
        self.root.app.user.set_book_page(page)

    def go_to_page_delete(self):
        self.selection = self.selection[:-1]
