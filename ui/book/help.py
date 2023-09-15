from ..braille import from_unicode


def _render(width, height, text):
    # text must already be i18n-ed to Unicode.
    data = []

    lines = tuple(from_unicode(line) for line in text.split('\n'))

    for line in lines:
        data.append(line)

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render_book_help(width, height):
    # TRANSLATORS: The AsciiDoc markup is used to suggest a page break
    # in this string.
    text = _('''\
With Canute 360 you can read files in Braille. You can move within a \
file using the three large control buttons on the front panel of \
Canute. Press the large button to the right of centre on the front \
panel labelled "forward" to move forward one page within this help \
file.

<<<

Press the large button to the left of centre, labelled "back" to move \
back one page within a file, similar to turning the pages in a \
physical book. You can move forwards of backwards five pages at a time \
by holding down the "forward" or "back" button. You can access all \
other Canute features, including the library menu, bookmarks and \
system settings by pressing the large central button labelled "menu" \
to access the main menu. Press the circular help button (labelled "H") \
at the top left of the display to return to your book.\
''')

    return _render(width, height, text)


def render_home_menu_help(width, height):
    text = _('''\
This is the main menu. From the main menu you can access the library, \
insert a bookmark, return to a bookmark that was previously placed \
within a file, or navigate to a page within a book. You can select an \
item from the main menu by pressing the triangular line select button \
to the left of the menu item on the display.

You can choose a new book by pressing the line select button to the \
left of "view library menu" on the display to access the library menu. \
You can navigate to a page within a file by pressing the triangular \
line select button to the left of "go to page" and following the \
instructions on the display. You can insert a bookmark by pressing the \
line select button to the left of "insert bookmark at current page". \
You can retrieve a bookmark by pressing the line select button to the \
left of "choose from existing bookmarks". To make system wide changes, \
including changing the language or Braille code, press the line select \
button to the left of "view system menu" on the display.\
''')

    return _render(width, height, text)
