import os
import grp
import pwd
import logging
import shutil

from ..actions import actions
from .. import utility
from .. import initial_state

log = logging.getLogger(__name__)


BOOK_EXTENSIONS = ('pef', 'brf', 'txt')


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
        user_state = await initial_state.read_user_state(library_dir)
        await store.dispatch(actions.set_user_state(user_state))
        await store.dispatch(actions.load_books('start'))
