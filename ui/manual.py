from .braille import from_unicode
from .book.book_file import BookFile, LoadState


manual_filename = '@@__canute_manual__@@'


def batch(a, n=9):
    return [a[i:i + n] for i in range(0, len(a), n)]


class Manual(BookFile):
    @property
    def title(self):
        # Since book titles are naively mapped from ASCII and since we
        # can only do that to SimBraille (currently!) the menu renderers
        # expect them in SimBraille.  So, I figure it's better to give a
        # naive-but-consistent SimBraille title here than a
        # decently-translated-but-inconsistent Unicode title.
        return 'canute manual'

    @staticmethod
    def create():
        # TRANSLATORS: Source text uses (minimal) AsciiDoc markup to give
        # formatting hints.  Since translation will generally alter width
        # and wrapping, these are just hints.  Interpretation of markup is
        # entirely up to you (no code processes it).
        text = _('''\
= Canute Quick Help

You can also access these contextual
help texts from anywhere by pressing
the topmost side button on the left.

== Book and Home Menu

Move through the book by pressing the

<<<

arrow buttons on the front of the
machine. Hold them down to move #e
pages at a time. The home menu shows
what you can do with the side buttons
from the home menu or the book. View
this by pressing the middle button on
the front. Pressing this button again
will always return you to your book.

<<<

== Bookmarks

Add a bookmark by pressing button #e
while in a book. Bookmarks are listed
here in the bookmark menu. Each bookmark
starts with the Canute page number based
on its #i line page. Go to the page by
selecting a bookmark by pressing one of
the side buttons. Holding the button

<<<

down will delete the bookmark.

== Go To Page Menu

Go to a page number by keying it in with
the side number buttons and pressing
forward. Pages are numbered based on the
#i line page height of the Canute. You
can delete entered numbers by pressing

<<<

or holding the back button. As always
you can go back to your current page by
pressing the menu button.

== Library Menu

Choose the book you wish to read by
pressing the button to the left of the
title. Use the arrow buttons to page

<<<

through the library. You can change the
ordering of the books in the system
menu.

== System Menu

Configure your preference on the sorting
order of books in the library and
bookmarks through the menu options. To

<<<

shutdown the Canute safely, select the
shutdown option and wait for #cj
seconds before unplugging it.
''')
        lines = text.split('\n')
        pages = batch(lines)
        pages = tuple(tuple(from_unicode(line) for line in page)
                      for page in pages)
        return Manual(manual_filename, 40, 9, pages=pages, load_state=LoadState.DONE)
