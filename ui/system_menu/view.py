from ..braille import format_title
from .system_menu import create
from .help import render_help


def render(width, height, state):
    if state.app.help_menu.visible:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state.app.help_menu.page, num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    menu_titles = create()

    page = state.app.system_menu.page
    data = list(menu_titles)
    # subtract title from page height
    data_height = height - 1
    max_pages = 1
    title = format_title(_('SYSTEM menu'), width, page, max_pages)
    n = page * data_height
    data = data[n: n + data_height]
    # pad page with empty rows
    while len(data) < data_height:
        data += (tuple(),)
    return tuple([title]) + tuple(data)
