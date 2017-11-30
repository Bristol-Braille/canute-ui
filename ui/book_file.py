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
                page = []
                pages = []
                for line in file:
                    line = line.replace('\n', '')
                    if FORM_FEED.match(line):
                        # pad up to the next page
                        while len(page) < self.height:
                            page.append('')
                        if line == '\f':
                            continue
                        else:
                            line = line.replace('\f', '')
                    if len(page) == self.height:
                        pages.append(tuple(page))
                        page = []
                    page.append(line)
                self.unconverted_pages = tuple(pages)
        elif self.ext == '.pef':
            xml_doc = minidom.parse(self.filename)
            xml_pages = xml_doc.getElementsByTagName('page')
            lines = []
            for page in xml_pages:
                for row in page.getElementsByTagName('row'):
                    try:
                        line = row.childNodes[0].data.rstrip()
                    except IndexError:
                        # empty row element
                        line = tuple()
                    lines.append(tuple(line))
            pages = []
            for i in range(len(lines))[::self.height]:
                page = lines[i:i + self.height]
                pages.append(tuple(page))
            self.unconverted_pages = tuple(pages)
        else:
            raise BookFileError(
                'Unexpected extension: {}'.format(self.ext))

    def open(self):
        if not self.is_open:
            log.debug('opening {}'.format(self.filename))
            pages = []
            for page in self.unconverted_pages:
                converted = (braille.to_braille(line) for line in page)
                pages.append(tuple(converted))
            self.pages = tuple(pages)
            self.is_open = True

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    @property
    def current_page_text(self):
        self.open()
        return self.pages[self.page_number]

    @property
    def max_pages(self):
        if self.ext == '.brf':
            return len(self.unconverted_pages) - 1
        else:
            self.open()
            return len(self.pages) - 1

    def set_page(self, page):
        if page < 0:
            self.page_number = 0
        elif page > self.max_pages:
            self.page_number = self.max_pages
        else:
            self.page_number = page
