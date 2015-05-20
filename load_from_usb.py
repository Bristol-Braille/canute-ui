#!/usr/bin/env python
from zipfile import ZipFile
import time
import argparse
import gzip
import logging
import os
import pwd
import grp
import subprocess
import shutil
import ui
from ui.utility import find_pef, find_firmware
from ConfigParser import ConfigParser, NoSectionError

log = logging.getLogger(__name__)

src_dir = 'ui'

'''
load_book: load new PEF books into the library when a usb disk is plugged in.

Works in conjuction with a udev rule.

Create a file at /etc/udev/rules.d/81-canute.rules with this content:
KERNEL=="sd?1", SUBSYSTEMS=="usb", RUN+="/path/to/load_from_usb.py --dev /dev/$kernel"

Where /path/to/load_book.py is this script.

Then: sudo /etc/init.d/udev restart

The default mount point is /mnt/books, which can be overridden with the --mount-point argument
'''

def mount_device(dev, mount_point):
    '''mount a device'''
    log.info("mounting %s on %s" % (dev, mount_point))
    subprocess.check_call(["mount", dev, mount_point])

def umount_device(mount_point):
    '''unmount a device'''
    log.info("umounting %s" % (mount_point))
    time.sleep(0.5)
    exit = subprocess.check_call(["umount", mount_point])
    if exit != 0:
        log.warning("umount status %s" % exit)

def get_bin_dir():
    return os.path.dirname(os.path.realpath(__file__)) + "/"

if __name__ == "__main__":

    log_file = get_bin_dir() + 'load_book.log'
    FORMAT = '%(asctime)s - %(levelname)-8s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, filename=log_file, format=FORMAT)
    log = logging.getLogger(__name__)

    # config
    config = ConfigParser()
    config.read(get_bin_dir() + src_dir + '/config.rc')

    canute_log_file = get_bin_dir() + src_dir + '/' + config.get('files', 'log_file')
    library_dir = config.get('files', 'library_dir')

    log.info("starting")

    parser = argparse.ArgumentParser(description="Load Book")

    parser.add_argument('--dev', action='store', dest='dev', help="device to mount", required=True)
    parser.add_argument('--update-firmware', action='store_const', const=True, dest='update_firmware', help="update firmware if file is found", default=False)
    parser.add_argument('--mount-point', action='store', dest='mount_point', help="where to mount", default="/mnt/books")
    parser.add_argument('--owner', action='store', dest='owner', help="new owner of the file", default="pi")

    args = parser.parse_args()

    try:
        uid = pwd.getpwnam(args.owner).pw_uid
        gid = grp.getgrnam(args.owner).gr_gid

        mount_device(args.dev, args.mount_point)

        # get the books
        books = find_pef(args.mount_point)

        # copy to library dir
        for filename in books:
            log.info("copying %s to %s" % (filename, library_dir))
            shutil.copy(filename, library_dir)

            # change ownership
            basename = os.path.basename(filename)
            new_path = library_dir + basename
            log.info("changing ownership of %s to %s to %s" % (new_path, uid, gid))
            os.chown(new_path, uid, gid)
        else:
            log.info("no books found")

        # copy the latest log file to the usb stick
        log.info("copying log file to usb stick")
        shutil.copy(canute_log_file, args.mount_point)

        # look for firmware
        if args.update_firmware:
            log.info("looking for new firmware...")
            firmware_file = find_firmware(args.mount_point)
            if firmware_file is not None:
                log.info("found firmware file %s" % firmware_file)
                log.info("removing everything in src dir %s" % get_bin_dir() + src_dir)
                shutil.rmtree(get_bin_dir() + src_dir)
                log.info("unzipping")
                with ZipFile(firmware_file) as zipfile:
                    zipfile.extractall(get_bin_dir())

                log.info("reboot")

    except Exception as e:
        log.warning("unexpected problem [%s]" % e)
    finally:
        # make sure we umount
        umount_device(args.mount_point)
