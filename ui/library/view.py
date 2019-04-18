from ..braille import from_ascii, format_title
from ..state_helpers import get_books


def render_help(width, height):
    data = []
    para = _('''\
Choose the book you wish to read by
pressing the button to the left of the
title. Use the arrow buttons to page
through the library. You can change the
ordering of the books in the system
menu.''')

    for line in para.split('\n'):
        data.append(from_ascii(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render_library(width, height, state):
    page = state['library']['page']
    books = get_books(state)
    # subtract title from page height
    data_height = height - 1
    max_pages = (len(books) // data_height) + 1
    title = format_title('library menu', width, page, max_pages)
    data = [title]
    n = page * data_height
    for book in books[n:n + data_height]:
        data.append(format_title(book.title, width, book.page_number,
                                 len(book.pages), capitalize=False))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page
    else:
        return render_library(width, height, state)
