from ui.utility import find_ui_update
from ui.config_loader import load
from ui.setup_logs import setup_logs
import os
import logging
from datetime import datetime
import shutil
import tarfile
import ui.initial_state

config = load("ui/config.rc")
log = setup_logs(config, logging.DEBUG)


def need_update():
    '''
    checks the state, if state is set to in_progress, get the update file and
    continue
    '''
    update_state = ui.initial_state.read()['app']['update_ui']
    log.info("update_ui = %s" % update_state)
    if update_state == "in progress":
        return True
    else:
        return False


def archive_and_untar():
    '''
    archive the ui directory in config's install_dir
    then untar.gz new archive into place
    '''
    install_dir = config.get('files', 'install_dir')
    install_dir = os.path.expanduser(install_dir)

    archive_dir = config.get('files', 'archive_dir')
    archive_dir = os.path.expanduser(archive_dir)

    log.info("archiving %s to %s" % (install_dir, archive_dir))
    archive_dir += datetime.now().strftime("%Y%m%d-%H%M%S-ui")
    shutil.move(install_dir, archive_dir)

    # untar new ui
    log.info("untar to %s" % install_dir)
    with tarfile.open(update_file, 'r:*') as archive:
        archive.extractall(install_dir)


if __name__ == '__main__':
    if not need_update():
        exit(0)

    update_file = find_ui_update(config)
    if update_file is None:
        log.warning("no update file found")
        exit(1)

    log.info("found update file: %s" % update_file)

    archive_and_untar()
