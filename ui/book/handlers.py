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
    return book._replace(file_contents=file_contents)


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
            pages.append(tuple(page))
    else:
        raise BookFileError(
            'Unexpected extension: {}'.format(book.ext))
    return book._replace(pages=tuple(pages))


async def get_page_data(book, store):
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

    return book.pages[book.page_number]


class BookFileError(Exception):
    pass
