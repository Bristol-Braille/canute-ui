import os
import re
import grp
import pwd
import logging
import shutil

from ..actions import actions
from ..store import store
from .. import convert
from .. import utility
from ..bookfile_list import BookFile_List


log = logging.getLogger(__name__)


NATIVE_EXTENSION = 'canute'
BOOK_EXTENSIONS = (NATIVE_EXTENSION, 'pef', 'brf')


def sync(state, library_dir):
    width, height = utility.dimensions(state['app'])
    convert_books(width, height, library_dir)
    library_files = [b['data'].filename for b in state['app']['books']]
    disk_files = utility.find_files(library_dir, (NATIVE_EXTENSION,))
    not_added = [f for f in disk_files if f not in library_files]
    if not_added != []:
        not_added_data = [BookFile_List(f, width) for f in not_added]
        store.dispatch(actions.add_books(not_added_data))
    non_existent = [f for f in library_files if f not in disk_files]
    if non_existent != []:
        store.dispatch(actions.remove_books(non_existent))


def convert_books(width, height, library_dir):
    file_names = utility.find_files(library_dir, BOOK_EXTENSIONS)
    for name in file_names:
        basename, ext = os.path.splitext(os.path.basename(name))
        if re.match('\.pef$', ext, re.I):
            log.info('converting pef to canute')
            native_file = library_dir + basename + '.' + NATIVE_EXTENSION
            convert.convert_pef(width, height, name, native_file)
        elif re.match('\.brf$', ext, re.I):
            log.info('converting brf to canute')
            native_file = library_dir + basename + '.' + NATIVE_EXTENSION
            convert.convert_brf(width, height, name, native_file)


def wipe(library_dir):
    for book in utility.find_files(library_dir, BOOK_EXTENSIONS):
        os.remove(book)


def replace(config, state):
    library_dir = config.get('files', 'library_dir')
    usb_dir = config.get('files', 'usb_dir')
    owner = config.get('user', 'user_name')
    wipe(library_dir)
    new_books = utility.find_files(usb_dir, BOOK_EXTENSIONS)
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
    sync(state, library_dir)
    store.dispatch(actions.replace_library('done'))
