from ..braille import from_ascii, format_title
from .handlers import get_page_data


def render_home_menu(width, height, book):
    data = []
    data.append(format_title(
        book.title, width, book.page_number, book.max_pages))
    data.append(from_ascii('go to page'))
    data.append(tuple())
    data.append(tuple())
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
    data.append(from_ascii('machine. Hold them down to move #e'))
    data.append(from_ascii('pages at a time. The home menu shows'))
    data.append(from_ascii('what you can do with the side buttons'))
    data.append(from_ascii('from the home menu or the book. View'))
    data.append(from_ascii('this by pressing the middle button on'))
    data.append(from_ascii('the front. Pressing this button again'))
    data.append(from_ascii('will always return you to your book.'))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height)
    home_menu = state['home_menu_visible']
    book_n = state['user']['current_book']
    book = state['user']['books'][book_n]
    if home_menu:
        return render_home_menu(width, height, book)
    else:
        return await get_page_data(book, store)
