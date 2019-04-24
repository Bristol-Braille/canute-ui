from ..braille import from_ascii


def render_help(width, height):
    data = []
    para = _('''\
Configure your preference on the sorting
order of books in the library and
bookmarks through the menu options. To
shutdown the Canute safely, select the
shutdown option and wait for #cj
seconds before unplugging it.''')

    for line in para.split('\n'):
        data.append(from_ascii(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)
