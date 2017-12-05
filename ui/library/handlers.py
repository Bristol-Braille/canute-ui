import os
import sys
import grp
import pwd
import logging
import shutil
import asyncio

from ..actions import actions
from .. import utility
from ..book_file import BookFile


log = logging.getLogger(__name__)


BOOK_EXTENSIONS = ('pef', 'brf')


@asyncio.coroutine
def sync(state, library_dir, store):
    width, height = utility.dimensions(state)
    library_files = [b.filename for b in state['books']]
    disk_files = utility.find_files(library_dir, BOOK_EXTENSIONS)
    not_added = [f for f in disk_files if f not in library_files]
    if not_added != []:
        not_added_books = []
        for f in not_added:
            book = BookFile(f, width, height)
            book = book.init()
            not_added_books.append(book)
        yield from store.dispatch(actions.add_books(not_added_books))
    non_existent = [f for f in library_files if f not in disk_files]
    if non_existent != []:
        yield from store.dispatch(actions.set_book(0))
        yield from store.dispatch(actions.remove_books(non_existent))


def wipe(library_dir):
    for book in utility.find_files(library_dir, BOOK_EXTENSIONS):
        os.remove(book)


@asyncio.coroutine
def replace(config, state, store):
    library_dir = config.get('files', 'library_dir')
    usb_dir = config.get('files', 'usb_dir')
    owner = config.get('user', 'user_name')
    new_books = utility.find_files(usb_dir, BOOK_EXTENSIONS)
    if len(new_books) > 0:
        wipe(library_dir)
        uid = pwd.getpwnam(owner).pw_uid
        gid = grp.getgrnam(owner).gr_gid
        for filename in new_books:
            log.info('copying {} to {}'.format(filename, library_dir))
            shutil.copy(filename, library_dir)

            # change ownership
            basename = os.path.basename(filename)
            new_path = library_dir + basename
            log.debug('changing ownership of {} from {} to {}'.format(
                new_path, uid, gid))
            os.chown(new_path, uid, gid)
        yield from sync(state, library_dir, store)
