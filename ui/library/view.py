from ..braille import format_title, from_unicode
from ..state_helpers import get_books


def render_help(width, height):
    data = []
    para = _('''\
This is the library menu. From this menu you can view and select from \
the files on the memory stick or SD card. You can choose a file by \
pressing the line select button to the left of the file name. Canute \
360 will then show your chosen file on the display. You can navigate \
forward and backwards within the library menu using the large buttons \
labelled "forward" and "back" on the front panel. You can return to \
the file you are currently reading by pressing the large central \
button labelled "menu".

To load a new file onto your Canute, first turn it off by pressing and \
then quickly releasing the small button to the right of the power \
socket on the back panel. Once the "please wait" text disappears, \
remove the memory stick or SD card you are using to store your files. \
Copy and paste your files, in BRF or PEF format, onto the memory stick \
or SD card using a computer. Finally, insert the USB stick or SD card \
into the slot on the side of Canute. Turn your Canute on again using \
the small button to the right of the power socket on the back panel. \
Once Canute has started your files will appear in the library menu.

For best results you should format your files with forty cells per \
line and nine lines of Braille per page. The latest version of Duxbury \
DBT and the free online robo-braille service both have a Canute 360 \
preset built in for formatting.\
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
