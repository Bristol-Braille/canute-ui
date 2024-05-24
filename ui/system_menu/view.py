from ..braille import format_title, from_unicode, alphas_to_unicodes
from . import upgrade
from .help import render_help
from .system import console, release, serial

async def render(width, height, state):
    if state.app.help_menu.visible:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state.app.help_menu.page, num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    menu_titles = tuple(map(from_unicode, (
        _('start console mode') if console else '',
        _('shutdown'),
        _('choose BRF encoding'),
        _('select language and code'),
        _('backup log to USB stick'),
        _('install upgrade from ') + alphas_to_unicodes(upgrade.source_name) if upgrade.available else '',
        release,
        serial,
    )))

    page = state.app.system_menu.page
    data = list(menu_titles)
    # subtract title from page height
    data_height = height - 1
    max_pages = 1
    title = format_title(_('system menu'), width, page, max_pages)
    n = page * data_height
    data = data[n: n + data_height]
    # pad page with empty rows
    while len(data) < data_height:
        data += (tuple(),)
    return tuple([title]) + tuple(data)
