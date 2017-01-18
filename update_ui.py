from subprocess import Popen, PIPE
from ui.utility import find_ui_update
from ui.config_loader import load
import os
import logging
from datetime import datetime
import shutil
import tarfile

'''
UI updater
'''

# setup the logs
log_format = logging.Formatter(
        '%(asctime)s - %(name)-16s - %(levelname)-8s - %(message)s')
log = logging.getLogger('')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)
fh = logging.FileHandler('update.log')
fh.setFormatter(log_format)
log.addHandler(fh)

'''
checks the state, if state is set to in_progress, get the update file and continue
'''
log.info("checking state")
process = Popen(["python", "ui/initial_state.py"], stdout=PIPE)
(update_state, err) = process.communicate()
exit_code = process.wait()

if update_state is None:
    log.warning("couldn't open state")
    exit(1)

update_state = update_state.strip()
log.info("update_ui = %s" % update_state)
if update_state != "in progress":
    exit(0)

config = load("ui/config.rc")
update_file = find_ui_update(config)
if update_file is None:
    log.warning("no update file found")
    exit(1)

log.info("found update file: %s" % update_file)

'''
everything is ready, so:
    * archive the ui directory in config's install_dir
    * untar.gz new archive into place
'''

install_dir = config.get('files', 'install_dir')
install_dir = os.path.expanduser(install_dir)

archive_dir = config.get('files', 'archive_dir')
archive_dir = os.path.expanduser(archive_dir)

# archive old ui
log.info("archiving %s to %s" % (install_dir, archive_dir))
archive_dir += datetime.now().strftime("%Y%m%d-%H%M%S-ui")
shutil.move(install_dir, archive_dir)

# untar new ui
log.info("untar to %s" % install_dir)
with tarfile.open(update_file, 'r:*') as archive:
    archive.extractall(install_dir)
