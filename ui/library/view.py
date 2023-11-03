import os
import math
import logging

from ..braille import from_unicode, from_ascii, truncate_middle, truncate_location, to_ueb_number, UNICODE_BRAILLE_BASE, unicodes_to_alphas

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


def file_display_text(file, width):
    title = os.path.splitext(file.name)[0].replace('_', ' ')
    if ord(title[0]) >= UNICODE_BRAILLE_BASE:
        title = unicodes_to_alphas(title)
    title = truncate_middle(title, width)
    return from_ascii(title)


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
        title = unicodes_to_alphas(title)
    # the 1 takes into account the trailing slash
    title = truncate_middle(dir_name, width - 1 - depth - extra)
    display = depth * '-' + title
    if extra > 0:
        # 1 takes into account the hyphen in extra
        pad = width + 1 - len(display) - extra
        display += ' ' + pad * '-' + ' ' + count_str
    return from_ascii(display)


class LibraryDisplay:
    def __init__(self, state, height):
        self.library = state.app.library
        self.DIRS_PAGE_SIZE = height - 1
        self.FILES_PAGE_SIZE = height - 2

    @property
    def _files_page_start(self):
        """only valid if files_dir_index is open"""
        return math.ceil((self.library.files_dir_index + 1) / self.DIRS_PAGE_SIZE)

    @property
    def _files_pages(self):
        return math.ceil(self.library.files_count / self.FILES_PAGE_SIZE)

    @property
    def _dirs_pages(self):
        return math.ceil(self.library.dir_count / self.DIRS_PAGE_SIZE)

    def _is_files_page(self, page_num):
        if self.library.files_page_open:
            files_pages = self._files_pages
            files_start = self._files_page_start
            return page_num >= files_start and page_num < files_start + files_pages
        return False

    def canonical_dir_page(self, page_num):
        if self.library.files_page_open and page_num >= self._files_page_start:
            # remove one extra to 'split' the current menu page and show it
            # before and after the current file list
            page_num -= min(self._files_pages, page_num - self._files_page_start) + 1
        return page_num

    def _page_display_text(self, dir, page, of_pages, width):
        title = unicodes_to_alphas(_('library menu'))
        progress = f'{to_ueb_number(page)}/{to_ueb_number(of_pages)}'
        if dir is not None:
            title += ' - ' + truncate_location(dir.relpath, width - len(title) - 3 - len(progress) - 3)
        title += ' ' + (width - len(title) - len(progress) - 2) * '-' + ' ' + progress
        return from_ascii(title)

    def _back_display_text(self):
        prev = 17 * '-' + ' ' + _('back to directory list')
        return from_unicode(prev)

    def _directories_display_text(self):
        next = 23 * '-' + ' ' + _('more directories')
        return from_unicode(next)


def render_library(width, height, state):
    display = LibraryDisplay(state, height)
    page_num = state.app.library.page

    begin = 0
    end = display.DIRS_PAGE_SIZE
    if display.library.files_page_open:
        if page_num == display._files_page_start - 1:
            end = display.library.files_dir_index % display.DIRS_PAGE_SIZE + 1
        if page_num == display._files_page_start + display._files_pages:
            begin = display.library.files_dir_index % display.DIRS_PAGE_SIZE

    if display._is_files_page(page_num):
        page_num -= display._files_page_start
        offset = page_num * display.FILES_PAGE_SIZE
        dir = display.library.open_dir
        yield display._page_display_text(dir, page_num + 1, dir.files_pages, width), None
        yield display._back_display_text(), None
        for i in range(0, display.FILES_PAGE_SIZE):
            if i >= begin and i < end and offset + i < len(dir.files):
                yield file_display_text(dir.files[offset + i], width), None
            else:
                yield tuple(), None
        return

    page_num = display.canonical_dir_page(page_num)
    start = page_num * display.DIRS_PAGE_SIZE
    yield display._page_display_text(
        display.library.dirs[start + begin].parent,
        page_num + 1, display._dirs_pages, width), None
    for i in range(0, display.DIRS_PAGE_SIZE):
        index = start + i
        if i >= begin and i < end and index < len(display.library.dirs):
            dir = display.library.dirs[index]
            yield dir_display_text(dir, width,
                display.library.files_dir_index != index), index if dir.files_count > 0 else None
        elif (i == 0 or i == display.DIRS_PAGE_SIZE - 1) and index < len(display.library.dirs):
            yield display._directories_display_text(), None
        else:
            yield tuple(), None


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
        display = list(render_library(width, height, state))
        return tuple([data[0] for data in display])
