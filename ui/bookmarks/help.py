from ..braille import from_ascii


def render_help(width, height):
    data = []

    para = _('''\
To navigate to a bookmark within a file, press the line select button \
immediately to the left of the desired bookmark. From the bookmark \
menu, you can also navigate to the beginning of the book by selecting \
"start of book" or the end of a book by selecting "end of book" using \
the line select buttons.''')

    for line in para.split('\n'):
        data.append(from_ascii(line))

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)
