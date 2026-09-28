from ..braille import (
    from_ascii, format_title, to_ueb_number, from_unicode,
    resolve_encoding, DEFAULT_ENCODING
)


def render_help(width, height):
    data = []
    para = _('''\
You can change the braille encoding by pressing the \
line select button to the left of your chosen encoding. \
The encoding will be used to display BRF files.
''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state):
    help_menu = state.app.help_menu.visible
    if help_menu:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state.app.help_menu.page, num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    enc = resolve_encoding(state.app.user.current_encoding)
    encodings = state.app.encoding.available
    enc_obj = encodings.get(enc, encodings[DEFAULT_ENCODING])
    current_enc = _(enc_obj.title)

    try:
        cur_index = list(encodings.keys()).index(enc)
    except ValueError:
        cur_index = -1

    # TRANSLATORS: A menu title, to which the encoding title is appended
    title = _('encoding:') + ' {}'
    title = format_title(
        title.format(current_enc),
        width, cur_index, len(encodings.keys()))
    data = [title]

    for enc in encodings:
        encs = list(encodings.keys()).index(enc)
        n = from_ascii(to_ueb_number(encs + 1) + ' ')
        data.append(n + tuple(from_unicode(_(encodings[enc].title))))

    while len(data) < height:
        data.append(tuple())

    return tuple(data)
