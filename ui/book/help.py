from ..braille import from_ascii


def _render(width, height, text):
    # text must already be i18n-ed.
    data = []

    lines = tuple(from_ascii(l) for l in text.split('\n'))

    for line in lines:
        data.append(line)

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render_book_help(width, height):
    text = _('''\
Move through the book by pressing the
arrow buttons on the front of the
machine. Hold them down to move #e
pages at a time. The home menu shows
what you can do with the side buttons
from the home menu or the book. View
this by pressing the middle button on
the front. Pressing this button again
will always return you to your book.''')
    return _render(width, height, text)


def render_home_menu_help(width, height):
    text = _('''\
(Main menu help text goes here.)''')
    return _render(width, height, text)
