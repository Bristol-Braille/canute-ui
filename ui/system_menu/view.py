from ..braille import from_ascii, format_title
from .system_menu import menu_titles
from ..i18n import I18n
from ..utility import get_user_locale

def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = [
        i18n._('Configure your preference on the sorting'),
        i18n._('order of books in the library and'),
        i18n._('bookmarks through the menu options. To'),
        i18n._('shutdown the Canute safely, select the'),
        i18n._('shutdown option and wait for #cj'),
        i18n._('seconds before unplugging it.'),
    ]

    data = [from_ascii(line) for line in data]

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'], state['user'].get('current_language', 'en_GB:en'))

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
