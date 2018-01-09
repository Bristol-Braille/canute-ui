import aiofiles
import asyncio
import logging
import re
import xml.dom.minidom as minidom


from ..actions import actions
from ..manual import manual
from .. import braille

log = logging.getLogger(__name__)

FORM_FEED = re.compile('\f')


async def init(book):
    if book.filename == manual.filename:
        return manual

    log.debug('initialiazing {}'.format(book.filename))

    async with aiofiles.open(book.filename) as f:
        file_contents = await f.read()
    if len(file_contents) == 0:
        raise BookFileError('File is empty: {}'.format(book.filename))

    return book._replace(file_contents=file_contents, pages=tuple())


def read_pages(book):
    if book.filename == manual.filename:
        return manual
    log.debug('reading pages {}'.format(book.filename))
    if book.ext == '.brf':
        page = []
        pages = []
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
        xml_doc = minidom.parseString(book.file_contents)
        xml_pages = xml_doc.getElementsByTagName('page')
        lines = []
        for page in xml_pages:
            for row in page.getElementsByTagName('row'):
                try:
                    line = row.childNodes[0].data.rstrip()
                except IndexError:
                    # empty row element
                    line = ''
                lines.append(braille.from_unicode(line))
        pages = []
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
                books = store.state['app']['user']['books']
                book = tuple(filter(lambda b: b.filename ==
                                    book.filename, books))[0]
                await asyncio.sleep(1)
        else:
            await store.dispatch(actions.set_book_loading(book))
            book = read_pages(book)
            await store.dispatch(actions.add_or_replace(book))

    return book.pages[page_number]


async def fully_load_books(state, store):
    state = store.state['app']
    if state['load_books'] == 'start':
        await store.dispatch(actions.load_books('loading'))
        books = state['user']['books']
        log.info('loading {} books'.format(len(books)))
        aborted = False
        for book in books:
            if len(book.pages) == 0:
                state = store.state['app']
                if state['load_books'] == 'cancel':
                    aborted = True
                    break
                try:
                    book = tuple(filter(lambda b: b.filename ==
                                        book.filename, state['user']['books']))[0]
                except IndexError:
                    continue
                if book.loading:
                    log.info('already loading {}, skipping'.format(book.title))
                    continue
                await store.dispatch(actions.set_book_loading(book))
                book = read_pages(book)
                await store.dispatch(actions.add_or_replace(book))
                await asyncio.sleep(0.1)
        await store.dispatch(actions.load_books(False))
        if aborted:
            log.info('loading books aborted')
        else:
            log.info('loading books done')


class BookFileError(Exception):
    pass
