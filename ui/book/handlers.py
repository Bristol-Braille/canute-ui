import aiofiles
import asyncio
import logging
import re
import xml.etree.cElementTree as ElementTree

from ..actions import actions
from ..manual import manual
from .. import braille
from .. import state_helpers
from . import book_file


log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def _read_pages(book, store, background=False):
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
                book = state_helpers.get_up_to_date_book(store, book)
            if len(page) > 0:
                # pad up to the end
                while len(page) < book.height:
                    page.append(tuple())
                pages.append(tuple(page))
            if book.load_state == book_file.LoadState.CANCEL:
                return book._replace(load_state=book_file.LoadState.INITIAL)
            if book.loading_in_background:
                await asyncio.sleep(0)
        elif book.ext == '.pef':
            xml_doc = ElementTree.fromstring(file_contents)

            if book.load_state == book_file.LoadState.CANCEL:
                return book._replace(load_state=book_file.LoadState.INITIAL)
            if book.loading_in_background:
                await asyncio.sleep(0)


            lines = []
            for page in xml_doc.iter('{http://www.daisy.org/ns/2008/pef}page'):
                for row in page.iter('{http://www.daisy.org/ns/2008/pef}row'):
                    line = ''.join(row.itertext()).rstrip()
                    lines.append(braille.from_unicode(line))

                book = state_helpers.get_up_to_date_book(store, book)
                if book.load_state == book_file.LoadState.CANCEL:
                    return book._replace(load_state=book_file.LoadState.INITIAL)
                if book.loading_in_background:
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
    except Exception as e:
        log.warning('book loading failed for {}'.format(book.filename))
        log.warning(e)
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
    if book.load_state == book_file.LoadState.LOADING:
        if book.loading_in_background != background:
            log.debug('switching loading of {} to background={}'.format(
                book.filename, background))
            book = book._replace(loading_in_background=background)
            await store.dispatch(actions.add_or_replace(book))
    elif book.load_state == book_file.LoadState.INITIAL:
        log.debug('loading {}, background={}'.format(
            book.filename, background))
        book = book._replace(loading_in_background=background,
                             load_state=book_file.LoadState.LOADING)
        await store.dispatch(actions.add_or_replace(book))
        book = await _read_pages(book, store)
        await store.dispatch(actions.add_or_replace(book))


prev_location = ''
prev_lib_page = -1
prev_book = ''
running_id = 0


async def load_books(store):
    global prev_location
    global prev_lib_page
    global prev_book
    global running_id

    state = store.state['app']
    location_changed = state['location'] != prev_location
    book_changed = state['user']['current_book'] != prev_book
    lib_page_changed = state['library']['page'] != prev_lib_page
    if location_changed or book_changed or lib_page_changed:
        task_id = running_id + 1
        running_id = task_id
        log.debug('starting load_books id:{}'.format(task_id))
        prev_location = state['location']
        prev_book = state['user']['current_book']
        prev_lib_page = state['library']['page']
        # load our current book as quickly as possible
        current_book = state_helpers.get_current_book(state)
        await _load(current_book, store)

        if running_id != task_id:
            log.debug('cancelling load_books id:{}'.format(task_id))
            return

        # load current library page books, in background unless we are actually in
        # the library
        background = not state['location'] == 'library'
        if background:
            await asyncio.sleep(1)
            if running_id != task_id:
                log.debug('cancelling load_books id:{}'.format(task_id))
                return
        lib_page = state['library']['page']
        log.info('loading books for page {}, background: {}'.format(lib_page, background))
        current_lib_page_books = state_helpers.get_books_for_lib_page(state, lib_page)
        for book in current_lib_page_books:
            book = state_helpers.get_up_to_date_book(store, book)
            await _load(book, store, background=background)
            if running_id != task_id:
                log.debug('cancelling load_books id:{}'.format(task_id))
                return

        # load other books that are within 5 library pages
        for i in range(1, 6):
            await asyncio.sleep(1)
            if running_id != task_id:
                log.debug('cancelling load_books id:{}'.format(task_id))
                return
            books = tuple()
            n = lib_page + i
            log.info('pre-loading books for page {}'.format(n))
            books += state_helpers.get_books_for_lib_page(state, n)
            n = lib_page - i
            if n >= 0:
                log.info('pre-loading books for page {}'.format(n))
                books += state_helpers.get_books_for_lib_page(state, n)
            for book in books:
                book = state_helpers.get_up_to_date_book(store, book)
                await _load(book, store, background=True)
                if running_id != task_id:
                    log.debug('cancelling load_books id:{}'.format(task_id))
                    return


class BookFileError(Exception):
    pass
