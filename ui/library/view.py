from ..braille import from_ascii, format_title
from ..state_helpers import get_books


def render_help_menu(width, height, page):
    data = [
        'Choose the book you wish to read by',
        'pressing the button to the left of the',
        'title. Use the arrow buttons to page',
        'through the library. You can change the',
        'ordering of the books in the system',
        'menu.',
    ]

    data = [from_ascii(line) for line in data]

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
        return render_help_menu(width, height, state['help_menu']['page'])
    else:
        return render_library(width, height, state)
