import os
import re
import xml.dom.minidom as minidom
from collections import namedtuple
import logging
import asyncio
import aiofiles

from . import braille
from .actions import actions

log = logging.getLogger(__name__)
FORM_FEED = re.compile('\f')


class BookFileError(Exception):
    pass


BookData = namedtuple(
    'BookData', 'filename width height page_number bookmarks file_contents unconverted_pages loading')
BookData.__new__.__defaults__ = (
    None, None, None, 0, tuple(), None, None, False)


class BookFile(BookData):
    async def init(self):
        log.debug('initialiazing {}'.format(self.filename))
        async with aiofiles.open(self.filename) as f:
            file_contents = await f.read()
        return self._replace(file_contents=file_contents)

    def read_pages(self):
        log.debug('reading pages {}'.format(self.filename))
        if self.ext == '.brf':
            page = []
            pages = []
            for line in self.file_contents.split('\n'):
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
            xml_doc = minidom.parseString(self.file_contents)
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

    async def current_page_text(self, store):
        if self.unconverted_pages:
            book = self
        elif self.loading:
            book = self
            while book.loading:
                books = store.state['app']['user']['books']
                book = tuple(filter(lambda b: b.filename ==
                                    book.filename, books))[0]
                await asyncio.sleep(1)
        else:
            await store.dispatch(actions.set_book_loading(self))
            book = self.read_pages()
            await store.dispatch(actions.add_or_replace(book))
        page = book.unconverted_pages[self.page_number]
        return tuple((braille.from_ascii(line) for line in page))

    @property
    def max_pages(self):
        if self.unconverted_pages:
            book = self
        else:
            book = self.read_pages()
        return len(book.unconverted_pages) - 1

    def set_page(self, page):
        if page < 0:
            page = 0
        elif page > self.max_pages:
            page = self.max_pages
        book = self._replace(page_number=page)
        return book
