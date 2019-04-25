from ..braille import format_title, from_unicode
from ..state_helpers import get_books


def render_help(width, height):
    data = []
    para = _('''\
This is the library menu. From this menu, you can view and select from \
the files loaded onto the memory stick or SD card. As with other menus, \
press the line select key to the left of a menu item to select it. \
Canute 360 will then display your chosen file on the reading surface. \
Navigate within the menu using the "forward" and "back" buttons. To load \
books onto your canute, first turn it off by pressing the button to the \
right of the power socket on the back panel. Once the "please wait" text \
disappears, remove the memory stick or SD card you are using. Copy and \
paste a BRF or PEF file onto the stick or card, using a computer, insert \
the stick or card into the slot. Turn your Canute on again, and once it \
has started your file will be in the library menu. As with all menus, \
select your file using the line select button to it's left. For best \
results, format BRF files with nine lines of forty cells per page in \
software. Duxbury DBT and RoboBraille have a Canute preset built in for \
formatting.\
''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render_library(width, height, state):
    page = state['library']['page']
    books = get_books(state)
    # subtract title from page height
    data_height = height - 1
    max_pages = (len(books) // data_height) + 1
    title = format_title(_('library menu'), width, page, max_pages)
    data = [title]
    n = page * data_height
    for book in books[n:n + data_height]:
        data.append(format_title(book.title, width, book.page_number,
                                 len(book.pages), capitalize=False))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page
    else:
        return render_library(width, height, state)
