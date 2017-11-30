from .braille import to_braille

contents = (
    '         canute quick help',
    '',
    'you can also acess these contextual',
    'help texts from anywhere by pressing',
    'the topmost side button on the left',
    '',
    '',
    '',
    '',
    '          book and home menu',
    '',
    'Move through the book by pressing the',
    'arrow buttons on the front of the',
    'machine. Hold them down to move 5 pages',
    'at a time. The home menu shows you what',
    'you can do with the side buttons from',
    'the home menu or the book. View this by',
    'pressing the middle button on the front.',
    'Pressing the menu button again will',
    'always return you to the book.',
    '',
    '',
    '          bookmarks',
    '',
    'Add a bookmark by pressing button 5',
    'while in a book. Bookmarks are listed',
    'here in the bookmark menu. Each bookmark',
    'starts with the Canute page number based',
    'on its 9 line page. Go to the page by',
    'selecting a bookmark by pressing one of',
    'the side buttons. Holding the button',
    'down will delete the bookmark.',
    '',
    '',
    '',
    '',
    '          go to page menu',
    '',
    'Go to a page number by keying it in with',
    'the side number buttons and pressing',
    'forward. Pages are numbered based on the',
    '9 line page height of the Canute. You',
    'can delete entered numbers by pressing',
    'or holding the back button. As always'
    'you can go back to your current page by',
    'pressing the menu button.',
    '          library menu',
    '',
    'Choose the book you wish to read by',
    'pressing the button to the left of the',
    'title. Use the arrow buttons to page',
    'through the library. You can change the',
    'ordering of the books in the system',
    'menu.',
    '',
    '          system menu',
    '',
    'Configure your preference on the sorting',
    'order of books in the library and',
    'bookmarks through the menu options. To',
    'shutdown the Canute safely, select the',
    'shutdown option and wait for 30 seconds',
    'before unplugging it.',
)

manual_filename = '@@__canute_manual__@@'


class Manual():
    page_number = 0
    bookmarks = tuple()
    filename = manual_filename
    title = 'canute manual'
    lines = tuple(to_braille(line) for line in contents)

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def max_pages(self):
        return (len(self.lines) - 1) // self.height

    @property
    def current_page_text(self):
        line_number = self.page_number * self.height
        return self.lines[line_number:line_number + self.height]

    def open(self):
        return

    def set_page(self, page):
        if page < 0:
            self.page_number = 0
        elif page > self.max_pages:
            self.page_number = self.max_pages
        else:
            self.page_number = page
