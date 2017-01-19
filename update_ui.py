from subprocess import Popen, PIPE
from ui.utility import find_ui_update
from ui.config_loader import load
from ui.setup_logs import setup_logs
import os
import logging
from datetime import datetime
import shutil
import tarfile

config = load("ui/config.rc")
log = setup_logs(config, logging.DEBUG)

'''
checks the state, if state is set to in_progress, get the update file and continue
'''
def need_update():
    log.info("checking state")
    process = Popen(["python", "ui/initial_state.py"], stdout=PIPE)
    (update_state, err) = process.communicate()
    exit_code = process.wait()

    if update_state is None:
        log.warning("couldn't open state")
        return False

    update_state = update_state.strip()
    log.info("update_ui = %s" % update_state)
    if update_state == "in progress":
        return True


'''
archive the ui directory in config's install_dir
then untar.gz new archive into place
'''
def archive_and_untar():
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
