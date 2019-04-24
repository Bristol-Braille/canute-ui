import textwrap
from ..braille import from_unicode, alphas_to_unicodes


def _render(width, height, text):
    # text must already be i18n-ed to Unicode.
    data = []

    lines = tuple(from_unicode(l) for l in text.split('\n'))

    for line in lines:
        data.append(line)

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render_book_help(width, height):
    text = _('''\
With Canute 360 you can read files in Braille, as well as insert, edit, \
and navigate to bookmarks.  To move within a file, use the three large \
control buttons on the front panel of Canute.  Press the large button to \
the right of centre on the front panel now, labelled "forward" in \
Braille to move forward one page within this file.  Press the large \
button to the left of centre, labelled "back" in Braille to move back \
one page within a file, similar to turning the pages in a physical book.  \
To access other features, including bookmarks, press the H button above \
line select button one, then press the large central button, labeled \
"menu" in Braille to access the main menu.\
''')
    if _(text) == text:
        text = textwrap.fill(text, width=width)
        text = alphas_to_unicodes(text)

    return _render(width, height, text)


def render_home_menu_help(width, height):
    text = _('''\
This is the main menu. From the main menu, you can access the library \
insert a bookmark at the current page, return to a bookmark that was \
previously placed within a file, or navigate to a page within a book. To \
select an item from the main menu, press the triangular line select \
button to the left of the menu item on the reading surface.  To choose a \
new book, press the line select button to the left of "view library \
menu". The library menu will then load.  To navigate to a page within \
the file, press the triangular line select button immediately to the \
left of "go to page" on the reading surface. A help screen will appear. \
Enter the page number using the numbered line select keys. Press the \
"forward" button to navigate to the selected page.  To insert a new \
bookmark at the current page, press the line select button to the left \
of "insert bookmark at current page". To retrieve a bookmark, press the \
line select button to the left of "choose from existing bookmarks".  A \
list of bookmarks within a file will display. You can select one using \
the line select buttons.\
''')
    if _(text) == text:
        text = textwrap.fill(text, width=width)
        text = alphas_to_unicodes(text)

    return _render(width, height, text)
