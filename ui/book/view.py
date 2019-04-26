from ..braille import from_ascii, format_title
from .handlers import get_page_data
from ..i18n import I18n
from .. import state_helpers
from .help import render_help


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


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    locale = state['user'].get('current_language', 'en_GB:en')
    if help_menu:
        return render_help(width, height)
    home_menu = state['home_menu_visible']
    book = state_helpers.get_current_book(state)
    if home_menu:
        return render_home_menu(width, height, book, locale)
    else:
        return await get_page_data(book, store)
