from ..braille import from_ascii, format_title, to_ueb_number
from ..book.handlers import get_page_data
from ..i18n import I18n

def render_help_menu(width, height, locale):
    i18n = I18n(locale)
    data = []

    data.append(from_ascii(i18n._('Add a bookmark by pressing button #e')))
    data.append(from_ascii(i18n._('while in a book. Bookmarks are listed')))
    data.append(from_ascii(i18n._('here in the bookmark menu. Each bookmark')))
    data.append(from_ascii(i18n._('starts with the Canute page number based')))
    data.append(from_ascii(i18n._('on its #i line page. Go to the page by')))
    data.append(from_ascii(i18n._('selecting a bookmark by pressing one of')))
    data.append(from_ascii(i18n._('the side buttons. Holding the button')))
    data.append(from_ascii(i18n._('down will delete the bookmark.')))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height, state['user'].get('current_language', 'en_GB:en'))

    book = state['user']['books'][state['user']['current_book']]
    page = state['bookmarks_menu']['page']

    line_n = page * (height - 1)
    bookmarks = book.bookmarks[line_n:line_n + (height - 1)]

    max_pages = (len(book.bookmarks) - 1) // (height - 1)
    title = format_title(
        'bookmarks: {}'.format(book.title),
        width, page, max_pages)
    data = [title]

    for bm in bookmarks:
        if bm == 0:
            data.append(from_ascii('start of book'))
        elif bm == book.max_pages:
            data.append(from_ascii('end of book'))
        elif bm == 'deleted':
            data.append(tuple())
        else:
            lines = await get_page_data(book, store, page_number=bm)
            line = lines[0]
            n = from_ascii(to_ueb_number(bm + 1) + ' ')
            data.append(n + tuple(line))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)
