from ..braille import from_ascii


def render_help(width, height):
    data = []

    para = _('''\
Move through the book by pressing the
arrow buttons on the front of the
machine. Hold them down to move #e
pages at a time. The home menu shows
what you can do with the side buttons
from the home menu or the book. View
this by pressing the middle button on
the front. Pressing this button again
will always return you to your book.
Here is another page of help.''')

    lines = tuple(from_ascii(l) for l in para.split('\n'))

    for line in lines:
        data.append(line)

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)
