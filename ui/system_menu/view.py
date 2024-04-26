import os
from ..braille import format_title, brailleify, from_unicode
from .help import render_help


# This exists on a Pi and reading it yields a useful board identifier.
# But existence will do for right now.
if os.path.exists('/sys/firmware/devicetree/base/model'):
    if os.path.exists('/etc/canute_release'):
        with open('/etc/canute_release') as x:
            release = brailleify(x.read().strip())
        with open('/etc/canute_serial') as x:
            serial = brailleify(x.read().strip())
    else:
        release = _('run in standalone mode')
        serial = release
else:
    # Assume we're being emulated.
    release = _('emulated')
    serial = release


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
        _('shutdown'),
        _('backup log to USB stick'),
        _('select language and code'),
        '',
        '',
        '',
        _('release:') + ' ' + release,
        _('serial:') + ' ' + serial,
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
