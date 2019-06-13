from ..braille import from_unicode


def render_help(width, height):
    data = []
    para = _('''\
This is the system menu. From the system menu you can make system wide \
changes to settings.

You can change the language or Braille code by pressing the line \
select button to the left of select language. Please note this will \
only change the system language or Braille code, not the language or \
code of any files in the library.\
''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)
