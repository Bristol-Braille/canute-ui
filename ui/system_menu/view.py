from ..braille import from_ascii, format_title
from .system_menu import create
from ..i18n import I18n


def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = []
    para = from_ascii(i18n._('''/
        Configure your preference on the sorting
        order of books in the library and
        bookmarks through the menu options. To
        shutdown the Canute safely, select the
        shutdown option and wait for #cj
        seconds before unplugging it.'''))

    lines = para.split('\n')

    for line in lines:
        data.append(line)

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    locale = state['user'].get('current_language', 'en_GB:en')
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'], locale)

    menu_titles = create(locale)

    page = state['system_menu']['page']
    data = list(menu_titles)
    # subtract title from page height
    data_height = height - 1
    max_pages = 1
    title = format_title('system menu', width, page, max_pages)
    n = page * data_height
    data = data[n: n + data_height]
    # pad page with empty rows
    while len(data) < data_height:
        data += (tuple(),)
    return tuple([title]) + tuple(data)
