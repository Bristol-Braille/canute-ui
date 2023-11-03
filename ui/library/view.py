import logging

from ..braille import from_unicode, from_ascii, truncate_middle, \
    truncate_location, to_ueb_number, UNICODE_BRAILLE_BASE, \
    unicodes_to_alphas, format_title

log = logging.getLogger(__name__)


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


def dir_display_text(dir, width, show_count=True):
    extra = 0
    if show_count:
        count = dir.files_count
        if count > 0:
            count_str = to_ueb_number(count)
            # 3 = ' - ' suffix
            extra = 3 + len(count_str)
    else:
        count_str = unicodes_to_alphas(_('go to book list'))
        extra = 3 + len(count_str)
    depth = dir._depth
    dir_name = dir.name.replace('_', ' ')
    if ord(dir_name[0]) >= UNICODE_BRAILLE_BASE:
        dir_name = unicodes_to_alphas(dir_name)
    # the 1 takes into account the trailing slash
    title = truncate_middle(dir_name, width - 1 - depth - extra)
    display = depth * '-' + title
    if extra > 0:
        # 1 takes into account the hyphen in extra
        pad = width + 1 - len(display) - extra
        display += ' ' + pad * '-' + ' ' + count_str
    return from_ascii(display)


def page_display_text(dir, page, of_pages, width):
    title = unicodes_to_alphas(_('library menu'))
    progress = f'{to_ueb_number(page)}/{to_ueb_number(of_pages)}'
    if dir is not None:
        title += ' - ' + truncate_location(dir.relpath, width - len(title) - 3 - len(progress) - 3)
    title += ' ' + (width - len(title) - len(progress) - 2) * '-' + ' ' + progress
    return from_ascii(title)


def back_display_text(width):
    back = unicodes_to_alphas(_('back to directory list'))
    prev = (width - len(back) - 1) * '-' + ' ' + back
    return from_ascii(prev)


def directories_display_text(width):
    more = unicodes_to_alphas(_('more directories'))
    next = (width - len(more) - 1) * '-' + ' ' + more
    return from_ascii(next)


def render_library(width, height, state):
    library = state.app.library
    page_num = library.page

    begin = 0
    end = library.DIRS_PAGE_SIZE
    if library.files_page_open:
        if page_num == library._files_page_start - 1:
            end = library.files_dir_index % library.DIRS_PAGE_SIZE + 1
        if page_num == library._files_page_start + library._files_pages:
            begin = library.files_dir_index % library.DIRS_PAGE_SIZE

    if library._is_files_page(page_num):
        page_num -= library._files_page_start
        offset = page_num * library.FILES_PAGE_SIZE
        dir = library.open_dir
        yield page_display_text(dir, page_num + 1, dir.files_pages, width)
        yield back_display_text(width)
        for i in range(0, library.FILES_PAGE_SIZE):
            if i >= begin and i < end and offset + i < len(dir.files):
                file = dir.files[offset + i]
                book = library.book_from_file(dir, file)
                yield format_title(book.title, width, book.page_number,
                                   book.get_num_pages(), capitalize=False)
            else:
                yield tuple()
        return

    page_num = library.canonical_dir_page(page_num)
    start = page_num * library.DIRS_PAGE_SIZE
    yield page_display_text(
        library.dirs[start + begin].parent,
        page_num + 1, library._dirs_pages, width)
    for i in range(0, library.DIRS_PAGE_SIZE):
        index = start + i
        if i >= begin and i < end and index < library.dir_count:
            dir = library.dirs[index]
            yield dir_display_text(dir, width,
                                   library.files_dir_index != index)
        elif (i == 0 or i == library.DIRS_PAGE_SIZE - 1) and index < library.dir_count:
            yield directories_display_text(width)
        else:
            yield tuple()


def render(width, height, state):
    if state.app.help_menu.visible:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state.app.help_menu.page, num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page
    else:
        return tuple(render_library(width, height, state))
