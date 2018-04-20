import aiofiles
import asyncio
import logging
import re
import xml.etree.ElementTree as ElementTree
import threading
from concurrent.futures import TimeoutError


from ..actions import actions
from ..manual import manual
from .. import braille

log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


async def init(book):
    if book.filename == manual.filename:
        return book

    log.debug('initialiazing {}'.format(book.filename))

    async with aiofiles.open(book.filename) as f:
        file_contents = await f.read()
    if len(file_contents) == 0:
        raise BookFileError('File is empty: {}'.format(book.filename))

    return book._replace(file_contents=file_contents, pages=tuple())

NS = {'pef': 'http://www.daisy.org/ns/2008/pef'}


async def read_pages(book):
    if book.filename == manual.filename:
        return book
    # if it has pages, it's already loaded
    if len(book.pages) > 0:
        return book
    log.debug('reading pages {}'.format(book.filename))
    pages = []
    if book.ext == '.brf':
        page = []
        for line in book.file_contents.splitlines():
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
        if len(page) > 0:
            # pad up to the end
            while len(page) < book.height:
                page.append(tuple())
            pages.append(tuple(page))
    elif book.ext == '.pef':
        xml_doc = ElementTree.fromstring(book.file_contents)
        xml_pages = xml_doc.findall('.//pef:page', NS)
        lines = []
        for page in xml_pages:
            for row in page.findall('.//pef:row', NS):
                line = ''.join(row.itertext()).rstrip()
                lines.append(braille.from_unicode(line))
        for i in range(len(lines))[::book.height]:
            page = lines[i:i + book.height]
            # pad up to the end
            while len(page) < book.height:
                page.append(tuple())
            pages.append(tuple(page))
    else:
        raise BookFileError(
            'Unexpected extension: {}'.format(book.ext))
    return book._replace(pages=tuple(pages))


async def get_page_data(book, store, page_number=None):
    if page_number is None:
        page_number = book.page_number
    if len(book.pages) == 0:
        if book.loading:
            while book.loading:
                # accessing store.state will get a fresh state
                book = store.state['app']['user']['books'][book.filename]
        else:
            await store.dispatch(actions.set_book_loading(book))
            book = await read_pages(book)
            await store.dispatch(actions.add_or_replace(book))

    if page_number >= len(book.pages):
        return book.pages[len(book.pages) - 1]

    return book.pages[page_number]


async def fully_load_books(store):
    state = store.state['app']
    if state['load_books'] == 'start':
        await store.dispatch(actions.load_books('loading'))
        books = state['user']['books']
        log.info('loading {} books'.format(len(books)))
        aborted = False
        tasks = []

        async def read(book):
            book = await read_pages(book)
            await store.dispatch(actions.add_or_replace(book))

        # gather tasks to reading books
        for filename in books:
            book = books[filename]
            if len(book.pages) == 0:
                state = store.state['app']
                if state['load_books'] == 'cancel':
                    aborted = True
                    break
                try:
                    book = state['user']['books'][filename]
                except IndexError:
                    continue
                if book.loading:
                    log.info('already loading {}, skipping'.format(book.title))
                    continue
                await store.dispatch(actions.set_book_loading(book))
                tasks.append(read(book))

        # run actual book reading on another thread as it hogs the event loop otherwise
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=loop.run_forever)
        future = asyncio.run_coroutine_threadsafe(
            asyncio.wait(tasks), loop=loop)
        thread.start()

        # check if the tasks are completed but don't hog this thread to wait
        # for that, asyncio.sleep instead
        while True:
            try:
                # check if the result is there, but don't wait very long at all
                # if it's there exit this loop
                future.result(timeout=0.00000000000000000000000000000001)
                break
            except TimeoutError:
                await asyncio.sleep(1)

        # seems to be the only way to close the event loop
        async def stop(loop):
            loop.stop()
        asyncio.run_coroutine_threadsafe(stop(loop), loop=loop)
        thread.join()

        await store.dispatch(actions.load_books(False))
        if aborted:
            log.info('loading books aborted')
        else:
            log.info('loading books done')


class BookFileError(Exception):
    pass
