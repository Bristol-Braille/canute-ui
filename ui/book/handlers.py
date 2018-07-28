import aiofiles
import asyncio
import logging
import re
import lxml.etree as ElementTree

from ..actions import actions
from ..manual import manual
from .. import braille
from .. import state_helpers
from . import book_file


log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def _read_pages(book, background=False):
    if book.filename == manual.filename:
        return book
    if book.load_state == book_file.LoadState.DONE:
        return book
    try:
        if book.ext == '.pef':
            mode = 'rb'
        else:
            mode = 'r'

        async with aiofiles.open(book.filename, mode) as f:
            file_contents = await f.read()

        if len(file_contents) == 0:
            log.warning('book empty {}'.format(book.filename))
            return book._replace(load_state=book_file.LoadState.FAILED)

        log.debug('reading pages {}'.format(book.filename))
        pages = []
        if book.ext == '.brf':
            page = []
            for line in file_contents.splitlines():
                if FORM_FEED.match(line):
                    # pad up to the next page
                    while len(page) < book.height:
                        page.append('')
                    if line == '\f':
                        continue
                    else:
                        line = line.replace('\f', '')
                if len(page) == book.height:
                    pages.append(tuple(page))
                    page = []
                page.append(braille.from_ascii(line))
                if background:
                    await asyncio.sleep(0)
            if len(page) > 0:
                # pad up to the end
                while len(page) < book.height:
                    page.append(tuple())
                pages.append(tuple(page))
        elif book.ext == '.pef':
            xml_doc = ElementTree.fromstring(file_contents)
            if background:
                await asyncio.sleep(0)
            xml_pages = xml_doc.findall('.//pef:page', NS)
            if background:
                await asyncio.sleep(0)
            lines = []
            for page in xml_pages:
                for row in page.findall('.//pef:row', NS):
                    line = ''.join(row.itertext()).rstrip()
                    lines.append(braille.from_unicode(line))
                if background:
                    await asyncio.sleep(0)
            for i in range(len(lines))[::book.height]:
                page = lines[i:i + book.height]
                # pad up to the end
                while len(page) < book.height:
                    page.append(tuple())
                pages.append(tuple(page))
        else:
            raise BookFileError(
                'Unexpected extension: {}'.format(book.ext))
        bookmarks = book.bookmarks
        if len(pages) > 1:
            # add an end-of-book bookmark
            bookmarks += (len(pages) - 1,)
        return book._replace(pages=tuple(pages),
                             load_state=book_file.LoadState.DONE,
                             bookmarks=bookmarks)
    except Exception:
        log.warning('book loading failed for {}'.format(book.filename))
        return book._replace(load_state=book_file.LoadState.FAILED)


async def get_page_data(book, store, page_number=None):
    if page_number is None:
        page_number = book.page_number

    while book.load_state != book_file.LoadState.DONE:
        await asyncio.sleep(0)
        # accessing store.state will get a fresh state
        book = store.state['app']['user']['books'][book.filename]

    if page_number >= len(book.pages):
        return book.pages[len(book.pages) - 1]

    return book.pages[page_number]


async def _load(book, store, background=False):
    await store.dispatch(actions.set_book_loading(book))
    if background:
        log.info('background loading {}'.format(book.filename))
    else:
        log.info('quickly loading {}'.format(book.filename))
    book = await _read_pages(book, background=background)
    await store.dispatch(actions.add_or_replace(book))


async def load_books(store):
    state = store.state['app']

    current_book = state_helpers.get_current_book(state)

    if current_book.load_state == book_file.LoadState.INITIAL:
        await _load(current_book, store)

    background = not state['location'] == 'library'
    books = state_helpers.get_books_for_lib_page(state)
    for book in books:
        if book.load_state == book_file.LoadState.INITIAL:
            await _load(book, store, background=background)


class BookFileError(Exception):
    pass
