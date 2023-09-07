import aiofiles
import asyncio
import logging
import re
import os
import xml.etree.cElementTree as ElementTree

from ..actions import actions
from ..manual import manual_filename
from .. import braille
from .. import state_helpers
from . import book_file
from . import indexer


log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def _read_pages2(book, background=False):
    '''Index `book`.
    If `background` is True, yield during long operations.
    If `book` is already loaded, does nothing.
    Upon return `book` will be in state DONE or FAILED.'''
    if book.filename == manual_filename:
        return book
    if book.load_state == book_file.LoadState.DONE:
        return book
    try:
        try:
            (r, w) = os.pipe2(os.O_CLOEXEC)
        except AttributeError:
            # macOS workaround as pipe2 not supported
            import fcntl
            (r, w) = os.pipe()
            fcntl.fcntl(r, fcntl.F_SETFD, fcntl.FD_CLOEXEC)
            fcntl.fcntl(w, fcntl.F_SETFD, fcntl.FD_CLOEXEC)
        indexer.trigger_load(book.filename, w)
        buf = None
        if background:
            os.set_blocking(r, False)
            while not buf:
                try:
                    buf = os.read(r, 10)
                except BlockingIOError:
                    await asyncio.sleep(0)
        else:
            os.set_blocking(r, True)
            buf = os.read(r, 10)
        if buf != b'ok':
            raise BookFileError(
                'loading failed: {}'.format(book.filename))
        log.info('loading complete for {}'.format(book.filename))
        bookmarks = book.bookmarks
        if indexer.get_page_count(book.filename) > 1:
            # add an end-of-book bookmark
            bookmarks += (indexer.get_page_count(book.filename) - 1,)
        return book._replace(load_state=book_file.LoadState.DONE,
                             bookmarks=bookmarks,
                             num_pages=indexer.get_page_count(book.filename),
                             indexed=True)
    except Exception:
        log.warning(f"book loading 2 failed for {book.filename}", exc_info=True)
        return book._replace(load_state=book_file.LoadState.FAILED)


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
            for line in file_contents.splitlines(keepends=True):
                if FORM_FEED.match(line):
                    # pad up to the next page
                    while len(page) < book.height:
                        page.append('')
                    continue
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
                             bookmarks=bookmarks,
                             indexed=False)
    except Exception:
        log.warning(f"book loading failed for {book.filename}", exc_info=True)
        return book._replace(load_state=book_file.LoadState.FAILED)


async def get_page_data(book, store, page_number=None):
    if page_number is None:
        page_number = book.page_number

    while book.load_state != book_file.LoadState.DONE:
        await asyncio.sleep(0)
        # accessing store.state will get a fresh state
        book = store.state['app']['user']['books'][book.filename]

    if not book.indexed:
        if page_number >= book.get_num_pages():
            return book.pages[book.get_num_pages() - 1]
        return book.pages[page_number]
    else:
        # FIXME FIXME: Explain how book's page number gets set to -1.
        page_number = min(indexer.get_page_count(book.filename) - 1,
                          page_number)
        if page_number == -1:
            page_number = max(0, page_number)
        page_extent = indexer.get_page(book.filename, page_number)
        # FIXME: 'with' is not the right idiom when fetching a page at a time.
        # Cache at least the file object for the current book.
        async with aiofiles.open(book.filename, 'rb') as f:
            await f.seek(page_extent.first)
            page = await f.read(page_extent.length)
            page = str(page, 'utf8')
            lines = []
            if book.ext == '.brf':
                for line in page.splitlines():
                    lines.append(braille.from_ascii(line))
            else:
                # FIXME: is it OK to assert?  Must state extensions and check call sites.
                assert(book.ext == '.pef')
                # Expand self-closing tags.
                page = re.sub(r'<row */>', r'<row></row>', page)
                # Get contents of all rows.
                for line in re.findall(r'(?<=<row>)[^<]*(?=</row>)', page):
                    lines.append(braille.from_unicode(line))
            while len(lines) < book.height:
                lines.append(tuple())
            return tuple(lines)


async def _load(book, store, background=False):
    await store.dispatch(actions.set_book_loading(book))
    if background:
        log.info('background loading {}'.format(book.filename))
    else:
        log.info('priority loading {}'.format(book.filename))
    book = await _read_pages2(book, background=background)
    await store.dispatch(actions.add_or_replace(book))


# Since handle_changes() spawns a new instance of this every time state
# changes, and since loading a book may take a while, be aware there may
# be multiple instances running concurrently (but not in parallel).
async def load_books(store, ev):
    '''Index all books discovered on media.
    The current book is loaded first, without yielding.
    Books visible on the current page of the library menu then get loaded
    asynchronously.  Finally all other books get loaded asynchronously.
    Upon completion all books will be in state DONE or state FAILED.
    `sem` is an async.Semaphore for limiting concurrency.  If it can't be
    acquired, the function returns.
    '''
    try:
        state = store.state['app']

        current_book = state_helpers.get_current_book(state)

        if current_book.load_state == book_file.LoadState.INITIAL:
            await _load(current_book, store)
            # Reload state in case we yielded.
            state = store.state['app']

        background = not state['location'] == 'library'

        while True:
            await ev.wait()
            ev.clear()
            state = store.state['app']
            books = state_helpers.get_books_for_lib_page(state)
            to_load = [b for b in books if b.load_state == book_file.LoadState.INITIAL]
            if not to_load:
                break
            await _load(to_load[0], store, background=background)
            # Reload state, in case we yielded and because _load() always updates
            # state.
            state = store.state['app']
            if books_loaded(state, state_helpers.get_books_for_lib_page(state)):
                log.info('all books on current library page indexed')
                break

        while True:
            await ev.wait()
            ev.clear()
            state = store.state['app']
            books = state_helpers.get_books(state)
            to_load = [b for b in books if b.load_state == book_file.LoadState.INITIAL]
            if not to_load:
                break
            await _load(to_load[0], store, background=background)
            # Reload state, in case we yielded and because _load() always updates
            # state.
            state = store.state['app']
            if books_loaded(state):
                log.info('all books indexed')
                return
    finally:
        pass


def books_loaded(state, books=None):
    if not books:
        books = state_helpers.get_books(state)
    return all(b.load_state == book_file.LoadState.DONE
               or b.load_state == book_file.LoadState.FAILED
               for b in books)


class BookFileError(Exception):
    pass
