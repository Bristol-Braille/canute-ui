from ..braille import from_unicode


def render_help(width, height):
    data = []

    para = _('''\
To navigate to a bookmark within a file press the line select button \
immediately to the left of your chosen bookmark. From the bookmark \
menu you can also navigate to the beginning of your book by selecting \
"start of book", or the end of a book by selecting "end of book", \
using the line select buttons. You can delete a bookmark by pressing \
and holding the line select button to the left of the bookmark you \
wish to delete for three seconds. You cannot delete the "start of \
book" or "end of book" bookmarks.\
''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    # pad page with empty rows
    while len(data) % height:
        data.append(tuple())

    return tuple(data)
