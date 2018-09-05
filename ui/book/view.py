from ..braille import from_ascii, format_title
from .handlers import get_page_data
from ..i18n import I18n
from .. import state_helpers


def render_home_menu(width, height, book, locale):
    i18n = I18n(locale)
    data = []
    data.append(format_title(book.title, width,
                             book.page_number, len(book.pages)))
    data.append(from_ascii(i18n._('go to page')))
    data.append(tuple())
    data.append(tuple())
    data.append(from_ascii(i18n._('insert bookmark at current page')))
    data.append(from_ascii(i18n._('choose from existing bookmarks')))
    data.append(tuple())
    data.append(from_ascii(i18n._('view system menu')))
    data.append(from_ascii(i18n._('view library menu')))
    return tuple(data)


def render_help_menu(width, height, locale):
    i18n = I18n(locale)
    data = []

    para = i18n._('''\
Move through the book by pressing the
arrow buttons on the front of the
machine. Hold them down to move #e
pages at a time. The home menu shows
what you can do with the side buttons
from the home menu or the book. View
this by pressing the middle button on
the front. Pressing this button again
will always return you to your book.''')

    lines = tuple(from_ascii(l) for l in para.split('\n'))

    for line in lines:
        data.append(line)

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    locale = state['user'].get('current_language', 'en_GB:en')
    if help_menu:
        return render_help_menu(width, height, locale)
    home_menu = state['home_menu_visible']
    book = state_helpers.get_current_book(state)
    if home_menu:
        return render_home_menu(width, height, book, locale)
    else:
        return await get_page_data(book, store)
