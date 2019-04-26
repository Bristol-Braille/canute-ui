from ..braille import from_ascii, format_title, to_ueb_number
from ..book.handlers import get_page_data
from .help import render_help


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help(width, height)

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
        elif bm == (len(book.pages) - 1):
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
