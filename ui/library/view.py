from ..braille import from_ascii, format_title
from ..i18n import I18n

def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = [
        i18n._('Choose the book you wish to read by'),
        i18n._('pressing the button to the left of the'),
        i18n._('title. Use the arrow buttons to page'),
        i18n._('through the library. You can change the'),
        i18n._('ordering of the books in the system'),
        i18n._('menu.'),
    ]

    data = [from_ascii(line) for line in data]

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render_library(width, height, state):
    page = state['library']['page']
    books = tuple(state['user']['books'].values())
    # subtract title from page height
    data_height = height - 1
    max_pages = (len(books) // data_height) + 1
    title = format_title('library menu', width, page, max_pages)
    data = [title]
    n = page * data_height
    for book in books[n:n + data_height]:
        data.append(format_title(book.title, width, book.page_number,
                                 book.max_pages, capitalize=False))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'], state['user'].get('current_language', 'en_GB:en'))
    else:
        return render_library(width, height, state)
