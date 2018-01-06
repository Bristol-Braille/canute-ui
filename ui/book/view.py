from ..braille import from_ascii, format_title
from .handlers import get_page_data


def render_home_menu(width, height, book):
    data = []
    data.append(format_title(
        book.title, width, book.page_number, book.max_pages))
    data.append(from_ascii('go to page'))
    data.append(from_ascii('go to start of book'))
    data.append(from_ascii('go to end of book'))
    data.append(from_ascii('insert bookmark at current page'))
    data.append(from_ascii('choose from existing bookmarks'))
    data.append(tuple())
    data.append(from_ascii('view system menu'))
    data.append(from_ascii('view library menu'))
    return tuple(data)


def render_help_menu(width, height):
    data = []

    data.append(from_ascii('Move through the book by pressing the'))
    data.append(from_ascii('arrow buttons on the front of the'))
    data.append(from_ascii('machine. Hold them down to move 5 pages'))
    data.append(from_ascii('at a time. The home menu shows you what'))
    data.append(from_ascii('you can do with the side buttons from'))
    data.append(from_ascii('the home menu or the book. View this by'))
    data.append(from_ascii('pressing the middle button on the front.'))
    data.append(from_ascii('Pressing the menu button again will'))
    data.append(from_ascii('always return you to the book.'))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height)
    home_menu = state['home_menu_visible']
    book_n = state['user']['book']
    book = state['user']['books'][book_n]
    if home_menu:
        return render_home_menu(width, height, book)
    else:
        return await get_page_data(book, store)
