from .braille import from_ascii
from .book_file import BookFile

pages = ((
    '         canute quick help',
    '',
    'you can also acess these contextual',
    'help texts from anywhere by pressing',
    'the topmost side button on the left',
    '',
    '',
    '',
    '',
), (
    '          book and home menu',
    '',
    'Move through the book by pressing the',
    'arrow buttons on the front of the',
    'machine. Hold them down to move #e',
    'pages at a time. The home menu shows',
    'what you can do with the side buttons',
    'from the home menu or the book. View',
    'this by pressing the middle button on',
), (
    'the front. Pressing this button again',
    'will always return you to your book.',
    '',
    '',
    '          bookmarks',
    '',
    'Add a bookmark by pressing button #e',
    'while in a book. Bookmarks are listed',
    'here in the bookmark menu. Each bookmark',
), (
    'starts with the Canute page number based',
    'on its #i line page. Go to the page by',
    'selecting a bookmark by pressing one of',
    'the side buttons. Holding the button',
    'down will delete the bookmark.',
    '',
    '',
    '',
    '',
), (
    '          go to page menu',
    '',
    'Go to a page number by keying it in with',
    'the side number buttons and pressing',
    'forward. Pages are numbered based on the',
    '#i line page height of the Canute. You',
    'can delete entered numbers by pressing',
    'or holding the back button. As always'
    'you can go back to your current page by',
), (
    'pressing the menu button.',
    '',
    '',
    '          library menu',
    '',
    'Choose the book you wish to read by',
    'pressing the button to the left of the',
    'title. Use the arrow buttons to page',
    'through the library. You can change the',
), (
    'ordering of the books in the system',
    'menu.',
    '',
    '',
    '          system menu',
    '',
    'Configure your preference on the sorting',
    'order of books in the library and',
    'bookmarks through the menu options. To',
), (
    'shutdown the Canute safely, select the',
    'shutdown option and wait for #cj',
    'seconds before unplugging it.',
    '',
    '',
    '',
    '',
    '',
    '',
),
)

pages = tuple(tuple(from_ascii(line) for line in page) for page in pages)

manual_filename = '@@__canute_manual__@@'


class Manual(BookFile):
    @property
    def title(self):
        return 'canute manual'


manual = Manual(manual_filename, 40, 9, pages=pages)
