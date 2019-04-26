from ..braille import from_ascii


def render_help(width, height):
    data = []

    para = _('''\
Add a bookmark by pressing button #e
while in a book. Bookmarks are listed
here in the bookmark menu. Each bookmark
starts with the Canute page number based
on its #i line page. Go to the page by
selecting a bookmark by pressing one of
the side buttons. Holding the button
down will delete the bookmark.''')

    for line in para.split('\n'):
        data.append(from_ascii(line))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)
