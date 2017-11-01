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
        self.filename = filename
        self.width = width
        self.height = height
        ext = os.path.splitext(filename)[-1].lower()

        if ext == '.brf':
            self.type = 'brf'
            pages = []
            page = []
            with open(filename) as file:
                for line in file:
                    line = line.replace('\n', '')
                    if FORM_FEED.match(line):
                        # pad up to the next page and ignore this line
                        while len(page) < height:
                            page.append('')
                        if line == '\f':
                            continue
                        else:
                            line = line.replace('\f', '')
                    if len(page) == height:
                        pages.append(tuple(page))
                        page = []
                    page.append(braille.to_braille(line))
            # pad the last page if it has at least one line
            if len(page) > 0:
                while len(page) < height:
                    page.append('')
                pages.append(tuple(page))
            self.pages = tuple(pages)

        elif ext == '.pef':
            self.type = 'pef'
            xml_doc = minidom.parse(filename)
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
            for i in range(len(lines))[::height]:
                page = lines[i:i + height]
                pages.append(tuple(page))
            self.pages = tuple(pages)

        else:
            raise BookFileError('Unexpected extension: {}'.format(ext))

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    @property
    def current_page_text(self):
        return self.pages[self.page_number]

    @property
    def max_pages(self):
        return len(self.pages) - 1

    def set_page(self, page):
        if page < 0:
            self.page_number = 0
        elif page > self.max_pages:
            self.page_number = self.max_pages
        else:
            self.page_number = page
