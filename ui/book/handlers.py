import aiofiles
import asyncio
import logging
import re
import os

from ..manual import manual_filename
from .. import braille
from .. import state_helpers
from . import book_file
from . import indexer


log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def _read_pages2(book, background=False):
    """Index `book`.
    If `background` is True, yield during long operations.
    If `book` is already loaded, does nothing.
    Upon return `book` will be in state DONE or FAILED."""
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
        os.close(r)
        os.close(w)
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
        log.warning(
            f'book loading 2 failed for {book.filename}', exc_info=True)
        return book._replace(load_state=book_file.LoadState.FAILED)


async def get_page_data(book, state, page_number=None):
    if page_number is None:
        page_number = book.page_number

    while book.load_state != book_file.LoadState.DONE:
        await asyncio.sleep(0)
        # accessing store.state will get a fresh state
        book = state.app.user.books[book.filename]

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
                assert book.ext == '.pef'
                # Expand self-closing tags.
                page = re.sub(r'<row */>', r'<row></row>', page)
                # Get contents of all rows.
                for line in re.findall(r'(?<=<row>)[^<]*(?=</row>)', page):
                    lines.append(braille.from_unicode(line))
            while len(lines) < book.height:
                lines.append(tuple())
            return tuple(lines)


async def load_book(book, state, background=False):
    state.app.library.set_book_loading(book)
    if background:
        log.info('background loading {}'.format(book.filename))
    else:
        log.info('priority loading {}'.format(book.filename))
    book = await _read_pages2(book, background=background)
    state.app.library.add_or_replace(book)


async def load_book_worker(state, queue):
    log.info('book indexing worker started')
    while True:
        relpath = await queue.get()
        book = state.app.user.books[relpath]
        if book.load_state == book_file.LoadState.INITIAL:
            log.debug(f'indexing book {relpath}')
            await load_book(book, state, background=True)
            log.debug('file indexing complete')
        queue.task_done()


def books_loaded(state, books=None):
    if not books:
        books = state_helpers.get_books(state)
    return all(b.load_state == book_file.LoadState.DONE
               or b.load_state == book_file.LoadState.FAILED
               for b in books)


class BookFileError(Exception):
    pass
