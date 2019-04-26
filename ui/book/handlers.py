import aiofiles
import asyncio
import logging
import re
import xml.etree.cElementTree as ElementTree

from ..actions import actions
from ..manual import manual_filename
from .. import braille
from .. import state_helpers
from . import book_file


log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def _read_pages(book, background=False):
    if book.filename == manual_filename:
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
        log.info('loading complete for {}'.format(book.filename))
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
        log.info('priority loading {}'.format(book.filename))
    book = await _read_pages(book, background=background)
    await store.dispatch(actions.add_or_replace(book))


# Since handle_changes() spawns a new instance of this every time state
# changes, and since loading a book may take a while, be aware there may
# be multiple instances running concurrently (but not in parallel).
async def load_books(store):
    state = store.state['app']

    current_book = state_helpers.get_current_book(state)

    if current_book.load_state == book_file.LoadState.INITIAL:
        await _load(current_book, store)
        # Reload state in case we yielded.
        state = store.state['app']

    background = not state['location'] == 'library'

    while True:
        books = state_helpers.get_books_for_lib_page(state)
        to_load = [b for b in books if b.load_state == book_file.LoadState.INITIAL]
        if not to_load:
            break
        await _load(to_load[0], store, background=background)
        # Reload state, in case we yielded and because _load() always updates
        # state.
        state = store.state['app']
        if all_books_loaded(state):
            log.info('all outstanding book loads complete')
            return


def all_books_loaded(state):
    books = state_helpers.get_books_for_lib_page(state)
    return all(b.load_state == book_file.LoadState.DONE
               or b.load_state == book_file.LoadState.FAILED
               for b in books)


class BookFileError(Exception):
    pass
