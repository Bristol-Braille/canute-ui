from ..braille import from_ascii, format_title
from ..i18n import I18n
from ..state_helpers import get_books


def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = []
    para = from_ascii(i18n._('''\
Choose the book you wish to read by
pressing the button to the left of the
title. Use the arrow buttons to page
through the library. You can change the
ordering of the books in the system
menu.'''))

    lines = para.split('\n')

    for line in lines:
        data.append(line)

    while len(data) < height:
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
        locale = state['user'].get('current_language', 'en_GB:en')
        return render_help_menu(width, height, state['help_menu']['page'], locale)
    else:
        return render_library(width, height, state)
