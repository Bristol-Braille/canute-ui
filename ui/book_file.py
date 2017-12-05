import os
import re
import xml.dom.minidom as minidom
from collections import namedtuple
import logging
import asyncio
import aiofiles

from . import braille

log = logging.getLogger(__name__)
FORM_FEED = re.compile('\f')


class BookFileError(Exception):
    pass

BookData = namedtuple('BookData', 'filename width height page_number bookmarks unconverted_pages')
BookData.__new__.__defaults__ = (None, None, None, 0, tuple(), None)


class BookFile(BookData):
    async def init(self):
        log.debug('initialiazing {}'.format(self.filename))
        if self.ext == '.brf':
            async with aiofiles.open(self.filename) as file:
                page = []
                pages = []
                async for line in file:
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
        elif self.ext == '.pef':
            async with aiofiles.open(self.filename) as file:
                contents = await file.read()
            xml_doc = minidom.parseString(contents)
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
        else:
            raise BookFileError(
                'Unexpected extension: {}'.format(self.ext))
        return self._replace(unconverted_pages=tuple(pages))

    @property
    def ext(self):
        return os.path.splitext(self.filename)[-1].lower()

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    @property
    def current_page_text(self):
        page = self.unconverted_pages[self.page_number]
        return tuple((braille.to_braille(line) for line in page))

    @property
    def max_pages(self):
        return len(self.unconverted_pages) - 1

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page > self.max_pages:
            page = self.max_pages
        book = self._replace(page_number=page)
        return book
