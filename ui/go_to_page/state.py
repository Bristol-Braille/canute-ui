import re

class GoToPageState:
    def __init__(self, root):
        self.root = root
        self.selection = ''
        self.keys_pressed = ''

    def go_to_page_set_selection(self):
        selection = self.selection + self.keys_pressed

        # handle delete ('<') characters
        r = re.compile(r'\d<')
        if r.search(selection) is not None:
            selection = ''
        # any left over delete characters after numbers are ignored
        selection = ''.join([c for c in selection if c != '<'])

        # overwrite characters when exceeding max page num width
        num_width = self.root.user.book.page_num_width
        selection = selection[-num_width:]

        self.selection = selection
        self.keys_pressed = ''
        # trigger redraw (unless confirming?)

    def go_to_page_key_press(self, value):
        self.keys_pressed += str(value)

    def go_to_page_confirm(self):
        self.go_to_page_set_selection()
        if self.selection == '':
            return
        page = int(self.selection) - 1
        self.selection = ''
        self.root.user.set_book_page(page)

    def go_to_page_delete(self):
        self.selection = self.selection[:-1]
