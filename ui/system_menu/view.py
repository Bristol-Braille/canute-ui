from ..braille import to_braille, format_title


def render_help_menu(width, height, page):
    data = [
        'Configure your preference on the sorting',
        'order of books in the library and',
        'bookmarks through the menu options. To',
        'shutdown the Canute safely, select the',
        'shutdown option and wait for 30 seconds',
        'before unplugging it.',
    ]

    data = [to_braille(line) for line in data]

    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'])

    page = state['system_menu']['page']
    data = state['system_menu']['data']
    # subtract title from page height
    data_height = height - 1
    max_pages = 1
    title = format_title('system menu', width, page, max_pages)
    n = page * data_height
    data = data[n: n + data_height]
    # pad page with empty rows
    while len(data) < data_height:
        data += ((0,) * width,)
    return tuple([title]) + tuple(data)
