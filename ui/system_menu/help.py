from ..braille import from_unicode


def render_help(width, height):
    data = []
    para = _('''\
This is the system menu.  From the system menu you can make system \
wide changes, such as changing the system language or shut down Canute''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)
