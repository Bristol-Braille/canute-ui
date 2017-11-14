import os
import re
import xml.dom.minidom as minidom
import logging

from . import braille

log = logging.getLogger(__name__)
FORM_FEED = re.compile('\f')


class BookFileError(Exception):
    pass


class BookFile():
    page_number = 0
    bookmarks = tuple()

    def __init__(self, filename, width, height):
        log.debug('initialiazing {}'.format(filename))
        self.filename = filename
        self.width = width
        self.height = height
        self.ext = os.path.splitext(filename)[-1].lower()
        self.is_open = False
        if self.ext == '.brf':
            with open(self.filename) as file:
                for line in file:
                    number_lines = sum(1 for line in file)

    def open(self):
        if not self.is_open:
            log.debug('opening {}'.format(self.filename))
            if self.ext == '.brf':
                pages = []
                page = []
                with open(self.filename) as file:
                    for line in file:
                        line = line.replace('\n', '')
                        if FORM_FEED.match(line):
                            # pad up to the next page and ignore this line
                            while len(page) < self.height:
                                page.append('')
                            if line == '\f':
                                continue
                            else:
                                line = line.replace('\f', '')
                        if len(page) == self.height:
                            pages.append(tuple(page))
                            page = []
                        page.append(braille.to_braille(line))
                # pad the last page if it has at least one line
                if len(page) > 0:
                    while len(page) < self.height:
                        page.append('')
                    pages.append(tuple(page))
                self.pages = tuple(pages)

            elif self.ext == '.pef':
                xml_doc = minidom.parse(self.filename)
                xml_pages = xml_doc.getElementsByTagName('page')
                lines = []
                for page in xml_pages:
                    for row in page.getElementsByTagName('row'):
                        try:
                            data = row.childNodes[0].data.rstrip()
                            line = []
                            for uni_char in data:
                                pin_num = braille.unicode_to_pin_num(uni_char)
                                line.append(pin_num)
                        except IndexError:
                            # empty row element
                            line = tuple()
                        lines.append(tuple(line))
                pages = []
                for i in range(len(lines))[::self.height]:
                    page = lines[i:i + self.height]
                    pages.append(tuple(page))
                self.pages = tuple(pages)
            else:
                raise BookFileError('Unexpected extension: {}'.format(ext))

            self.is_open = True


    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    @property
    def current_page_text(self):
        if not self.is_open:
            self.open()
        return self.pages[self.page_number]

    @property
    def max_pages(self):
        if not self.is_open:
            self.open()
        return len(self.pages) - 1

    def set_page(self, page):
        if not self.is_open:
            self.open()
        if page < 0:
            self.page_number = 0
        elif page > self.max_pages:
            self.page_number = self.max_pages
        else:
            self.page_number = page
