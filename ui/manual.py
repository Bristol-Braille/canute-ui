from .braille import from_ascii
from .book.book_file import BookFile, LoadState
from .i18n import I18n
import os

i18n = I18n()

manual_filename = '@@__canute_manual__@@'

class Manual(BookFile):
    @property
    def title(self):
        return i18n._('canute manual')

    @staticmethod
    def create():
        pages = ((
            i18n._('         canute quick help'),
            '',
            i18n._('you can also acess these contextual'),
            i18n._('help texts from anywhere by pressing'),
            i18n._('the topmost side button on the left'),
            '',
            '',
            '',
            '',
        ), (
            i18n._('          book and home menu'),
            '',
            i18n._('Move through the book by pressing the'),
            i18n._('arrow buttons on the front of the'),
            i18n._('machine. Hold them down to move #e'),
            i18n._('pages at a time. The home menu shows'),
            i18n._('what you can do with the side buttons'),
            i18n._('from the home menu or the book. View'),
            i18n._('this by pressing the middle button on'),
        ), (
            i18n._('the front. Pressing this button again'),
            i18n._('will always return you to your book.'),
            '',
            '',
            i18n._('          bookmarks'),
            '',
            i18n._('Add a bookmark by pressing button #e'),
            i18n._('while in a book. Bookmarks are listed'),
            i18n._('here in the bookmark menu. Each bookmark'),
        ), (
            i18n._('starts with the Canute page number based'),
            i18n._('on its #i line page. Go to the page by'),
            i18n._('selecting a bookmark by pressing one of'),
            i18n._('the side buttons. Holding the button'),
            i18n._('down will delete the bookmark.'),
            '',
            '',
            '',
            '',
        ), (
            i18n._('          go to page menu'),
            '',
            i18n._('Go to a page number by keying it in with'),
            i18n._('the side number buttons and pressing'),
            i18n._('forward. Pages are numbered based on the'),
            i18n._('#i line page height of the Canute. You'),
            i18n._('can delete entered numbers by pressing'),
            i18n._('or holding the back button. As always'),
            i18n._('you can go back to your current page by'),
        ), (
            i18n._('pressing the menu button.'),
            '',
            '',
            i18n._('          library menu'),
            '',
            i18n._('Choose the book you wish to read by'),
            i18n._('pressing the button to the left of the'),
            i18n._('title. Use the arrow buttons to page'),
            i18n._('through the library. You can change the'),
        ), (
            i18n._('ordering of the books in the system'),
            i18n._('menu.'),
            '',
            '',
            i18n._('          system menu'),
            '',
            i18n._('Configure your preference on the sorting'),
            i18n._('order of books in the library and'),
            i18n._('bookmarks through the menu options. To'),
        ), (
            i18n._('shutdown the Canute safely, select the'),
            i18n._('shutdown option and wait for #cj'),
            i18n._('seconds before unplugging it.'),
            '',
            '',
            '',
            '',
            '',
            '',
        ),
        )
        pages = tuple(tuple(from_ascii(line) for line in page) for page in pages)
        return Manual(manual_filename, 40, 9, pages=pages, load_state=LoadState.DONE)