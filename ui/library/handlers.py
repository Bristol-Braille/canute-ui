import os
import grp
import pwd
import logging
import shutil
import asyncio

from ..actions import actions
from .. import utility
from ..book.handlers import init

log = logging.getLogger(__name__)


BOOK_EXTENSIONS = ('pef', 'brf')


async def sync(state, library_dir, store):
    log.info('syncing library')
    width, height = utility.dimensions(state)
    books = state['user']['books']
    for book in books:
        try:
            book = await init(book)
        except Exception as e:
            log.warning('could not open {}'.format(book.filename))
            log.warning(e)
            await store.dispatch(actions.remove_books([book.filename]))
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
