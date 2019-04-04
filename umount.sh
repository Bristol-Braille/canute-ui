#!/bin/sh
# Install as /usr/local/sbin/umount.sh
# In concert with udev rule this unmounts block devices that get removed
# without warning, to clean up the mount table and ensure that subsequent media
# using the port do generate fresh mount notifications.
logger --stderr "Brute umount of $DEVNAME"
exec umount $DEVNAME
