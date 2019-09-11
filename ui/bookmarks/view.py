from ..braille import from_ascii, from_unicode, format_title, to_ueb_number
from ..book.handlers import get_page_data
from .help import render_help


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    book = state['user']['books'][state['user']['current_book']]
    page = state['bookmarks_menu']['page']

    line_n = page * (height - 1)
    bookmarks = book.bookmarks[line_n:line_n + (height - 1)]

    # Account for title at the top in maths.
    bookmark_lines = height - 1
    num_pages = (len(book.bookmarks) + (bookmark_lines-1)) // bookmark_lines
    # TRANSLATORS: Bookmarks menu title; gets followed by book name
    title = _('bookmarks:') + ' {}'
    title = format_title(
        title.format(book.title),
        width, page, num_pages)
    data = [title]

    for bm in bookmarks:
        if bm == 0:
            data.append(from_unicode(_('start of book')))
        elif bm == (book.get_num_pages() - 1):
            data.append(from_unicode(_('end of book')))
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
