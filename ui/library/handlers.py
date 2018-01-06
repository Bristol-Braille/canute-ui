import os
import grp
import pwd
import logging
import shutil
import asyncio

from ..actions import actions
from .. import utility
from ..book.handlers import init
from ..book_file import BookFile


log = logging.getLogger(__name__)


BOOK_EXTENSIONS = ('pef', 'brf')


async def sync(state, library_dir, store):
    log.info('syncing library')
    width, height = utility.dimensions(state)
    books = state['user']['books']
    library_files = [b.filename for b in books]
    disk_files = utility.find_files(library_dir, BOOK_EXTENSIONS)
    disk_files.sort(key=str.lower)
    non_existent = [f for f in library_files if f not in disk_files]
    if non_existent != []:
        await store.dispatch(actions.set_book(0))
        await store.dispatch(actions.remove_books(non_existent))
    books = [b for b in books if b.filename not in non_existent]
    not_added = (f for f in disk_files if f not in library_files)
    not_added_books = [BookFile(f, width, height) for f in not_added]
    books += not_added_books
    for book in books:
        try:
            book = await init(book)
        except:
            log.warning('could not open {}'.format(book.filename))
        else:
            await store.dispatch(actions.add_or_replace(book))
    await store.dispatch(actions.load_books('start'))


def wipe(library_dir):
    for book in utility.find_files(library_dir, BOOK_EXTENSIONS):
        os.remove(book)


async def replace(config, state, store):
    log.info('replacing library')
    library_dir = config.get('files', 'library_dir')
    usb_dir = config.get('files', 'usb_dir')
    owner = config.get('user', 'user_name')
    new_books = utility.find_files(usb_dir, BOOK_EXTENSIONS)
    if len(new_books) > 0:
        wipe(library_dir)
        uid = pwd.getpwnam(owner).pw_uid
        gid = grp.getgrnam(owner).gr_gid
        for filename in new_books:
            log.debug('copying {} to {}'.format(filename, library_dir))
            shutil.copy(filename, library_dir)

            # change ownership
            basename = os.path.basename(filename)
            new_path = library_dir + basename
            log.debug('changing ownership of {} from {} to {}'.format(
                new_path, uid, gid))
            os.chown(new_path, uid, gid)
            asyncio.sleep(0.1)
        await sync(state, library_dir, store)
