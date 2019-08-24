from ..braille import from_unicode, format_title
from .handlers import get_page_data
from .. import state_helpers
from .help import render_book_help, render_home_menu_help


def render_home_menu(width, height, book, locale):
    data = []
    data.append(format_title(book.title, width,
                             book.page_number, book.get_num_pages()))
    data.append(from_unicode(_('go to page')))
    data.append(tuple())
    data.append(tuple())
    data.append(from_unicode(_('insert bookmark at current page')))
    data.append(from_unicode(_('choose from existing bookmarks')))
    data.append(tuple())
    data.append(from_unicode(_('view system menu')))
    data.append(from_unicode(_('view library menu')))
    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    home_menu = state['home_menu_visible']
    locale = state['user'].get('current_language', 'en_GB:en')
    if help_menu:
        if home_menu:
            all_lines = render_home_menu_help(width, height)
        else:
            all_lines = render_book_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page
    book = state_helpers.get_current_book(state)
    if home_menu:
        return render_home_menu(width, height, book, locale)
    else:
        return await get_page_data(book, store)
