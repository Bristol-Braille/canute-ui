import logging
import aiofiles
from collections import OrderedDict
import toml
import os

from .manual import Manual, manual_filename
from .cleaning_and_testing import CleaningAndTesting, cleaning_filename
from .book.book_file import BookFile
from .library.explorer import Library, Directory, LocalFile
from .i18n import install, DEFAULT_LOCALE, OLD_DEFAULT_LOCALE

from . import config_loader

STATE_FILE = 'state.pkl'
USER_STATE_FILE = 'canute_state.txt'

manual = Manual.create()

log = logging.getLogger(__name__)


def to_state_file(book_path):
    basename = os.path.basename(book_path)
    dirname = os.path.dirname(book_path)
    return os.path.join(dirname, 'canute.' + basename + '.txt')


def configured_source_dirs():
    config = config_loader.load()
    return config.get('files', {}).get('library', [])


def mounted_source_paths(media_dir, only_mounted=False):
    """
    return mounted mount points and, by default, any non-mountpoint paths
    """
    for source_dir in configured_source_dirs():
        source_path = os.path.join(media_dir, source_dir.get('path'))
        if (source_dir.get('mountpoint', False) and os.path.ismount(source_path)) or \
                (not only_mounted and not source_dir.get('mountpoint', False)):
            yield source_path, source_dir.get('swappable', False)


def swappable_usb(data):
    """
    The state file contains part of the book path (e.g. usb0) and so if we want
    to maintain compatibility with the old standalone setup, we need to convert
    it to something it understands.  So here we fix any 'swappable' path (i.e.
    USB removable media) to 'front-usb' and rely on the function below to find
    the correct prefix on app startup.
    """
    book = data.get('current_book')
    if book is not None:
        for source_dir in configured_source_dirs():
            if source_dir.get('swappable', False):
                prefix = source_dir.get('path') + os.sep
                if book.startswith(prefix):
                    book = os.path.join('front-usb', book[len(prefix):])
                    # modifying data is safe as a new dict is created each time
                    data['current_book'] = book
                    break
    return data


def swap_library(current_book, books):
    """
    The current_book path includes a mount-point subpath (if on removable media)
    so try to cope with user accidentally swapping slots
    """
    config = config_loader.load()
    library = config.get('files', {}).get('library', [])

    # check for expected path, for backward compatibility with standalone unit
    for path in ['front-usb' + os.path.sep, 'back-usb' + os.path.sep]:
        if current_book.startswith(path):
            rel_book = current_book[len(path):]
            break

    # see if we can find it on a different swappable device path
    for lib in library:
        if lib.get('swappable', False):
            path = lib['path']
            book = os.path.join(path, rel_book)
            if book in books:
                return book


async def read_user_state(media_dir, state):
    global manual
    current_book = manual_filename
    current_language = None

    # walk the available filesystems for directories and braille files
    library = Library(media_dir, configured_source_dirs(), ('brf', 'pef'))
    book_files = library.book_files()

    source_paths = mounted_source_paths(media_dir)
    for source_path, swappable in source_paths:
        main_toml = os.path.join(source_path, USER_STATE_FILE)
        if os.path.exists(main_toml):
            try:
                main_state = toml.load(main_toml)
                if 'current_book' in main_state:
                    current_book = main_state['current_book']
                if 'current_language' in main_state:
                    current_language = main_state['current_language']
                log.info(f'loaded {main_toml}')
                break
            except Exception:
                log.warning(f'user state loading failed for {main_toml}, ignoring')

    if not current_language or current_language == OLD_DEFAULT_LOCALE:
        current_language = DEFAULT_LOCALE

    install(current_language)
    manual = Manual.create()

    manual_toml = os.path.join(media_dir, to_state_file(manual_filename))
    if os.path.exists(manual_toml):
        try:
            t = toml.load(manual_toml)
            if 'current_page' in t:
                manual = manual._replace(page_number=t['current_page'] - 1)
            if 'bookmarks' in t:
                manual = manual._replace(bookmarks=tuple(sorted(manual.bookmarks + tuple(
                    bm - 1 for bm in t['bookmarks']))))
        except Exception:
            log.warning(
                'manual state loading failed for {}, ignoring'.format(manual_toml))

    width, height = state.app.dimensions

    books = OrderedDict({manual_filename: manual})
    for book_file in book_files:
        filename = os.path.join(media_dir, book_file)
        toml_file = to_state_file(filename)
        book = BookFile(filename=filename, width=width, height=height)
        if os.path.exists(toml_file):
            try:
                t = toml.load(toml_file)
                if 'current_page' in t:
                    book = book._replace(page_number=t['current_page'] - 1)
                if 'bookmarks' in t:
                    book = book._replace(bookmarks=tuple(sorted(book.bookmarks + tuple(
                        bm - 1 for bm in t['bookmarks']))))
            except Exception as err:
                log.error(err)
                log.warning(
                    'book state loading failed for {}, ignoring'.format(toml_file))
        # else: no file exists, so just use the defaults
        books[book_file] = book
    books[cleaning_filename] = CleaningAndTesting.create()

    home_dir = Directory('canute 360')
    home_dir.files = [LocalFile(manual_filename), LocalFile(cleaning_filename)]
    library.dirs.insert(0, home_dir)

    if current_book not in books:
        # let's check that they're not just using a different USB port
        log.info('current book not in original library {}'.format(current_book))
        current_book = swap_library(current_book, books)
        if current_book not in books:
            log.warn('current book not found {}, ignoring'.format(current_book))
            current_book = manual_filename

    state.app.user.books = books
    state.app.library.media_dir = media_dir
    state.app.library.dirs = library.dirs
    state.app.user.load(current_book, current_language)


async def read(media_dir, state):
    await read_user_state(media_dir, state)


async def write(media_dir, queue):
    log.info('save file worker started')
    while True:
        (filename, data) = await queue.get()
        log.debug(f'save requested for {filename}')
        s = toml.dumps(swappable_usb(data))

        if filename is None:
            # main user state file
            source_paths = mounted_source_paths(media_dir)
            for source_path, swappable in source_paths:
                path = os.path.join(source_path, USER_STATE_FILE)
                log.debug('writing user state file save to {path}')
                async with aiofiles.open(path, 'w') as f:
                    await f.write(s)

        else:
            # book state file
            if filename == manual_filename:
                path = os.path.join(media_dir, path)
            else:
                path = to_state_file(filename)
            log.debug(f'writing {filename} state file save to {path}')
            async with aiofiles.open(path, 'w') as f:
                await f.write(s)

        log.debug('state file save complete')
        queue.task_done()
