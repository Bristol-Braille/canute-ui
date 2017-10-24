from ..braille import to_braille, format_title
from .. import utility


def render_help_menu(width, height, page):
    data = [
        'Choose the book you wish to read by',
        'pressing the button to the left of the',
        'title. Use the arrow buttons to page',
        'through the library. You can change the',
        'ordering of the books in the system',
        'menu.',
    ]

    data = [to_braille(line) for line in data]

    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)


def render_library(width, height, state):
    page = state['library']['page']
    books = state['books']
    # subtract title from page height
    data_height = height - 1
    max_pages = utility.get_max_pages(books, data_height)
    title = format_title('library menu', width, page, max_pages)
    data = [title]
    n = page * data_height
    for book in books[n:n + data_height]:
        max_pages = utility.get_max_pages(book, height)
        data.append(format_title(book.title, width, book.page,
                                 max_pages, capitalize=False))

    # pad page with empty rows
    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'])
    else:
        return render_library(width, height, state)
