from ..braille import from_ascii, format_title
from ..i18n import I18n
from ..utility import get_user_locale

def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = (
        i18n._('Go to a page number by keying it in with'),
        i18n._('the side number buttons and pressing'),
        i18n._('forward. Pages are numbered based on the'),
        i18n._('#i line page height of the Canute. You'),
        i18n._('can delete entered numbers by pressing'),
        i18n._('or holding the back button. As always'),
        i18n._('you can go back to your current page by'),
        i18n._('pressing the menu button.'),
    )

    data = [from_ascii(line) for line in data]

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'], state['user'].get('current_language', 'en_GB:en'))

    data = [from_ascii(i18n._('enter page number using the side buttons'))]

    try:
        book = state['user']['books'][state['user']['current_book']]
    except IndexError:
        book = None

    if book is None:
        total_pages = 0
        page = 0
        title_text = 'no book'
    else:
        total_pages = book.max_pages
        page = book.page_number
        title_text = book.title

    data.append(format_title(
        title_text, width, page, total_pages))

    selection = state['go_to_page']['selection']
    if selection == '':
        selection = -1
    else:
        selection = int(selection) - 1

    t = format_title(i18n._('go to page number'), width,
                     selection, total_pages, capitalize=False)
    data.append(t)

    data.append(from_ascii(i18n._('please confirm by pressing forward')))
    data.append(from_ascii(i18n._('undo by pressing back')))
    data.append(from_ascii(i18n._('to go back to book press middle button')))

    for _ in range(height - 6):
        data.append(tuple())

    return tuple(data)
