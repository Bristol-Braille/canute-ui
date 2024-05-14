#!/usr/bin/env python3
#
# Monitor removeable block devices and notify UI of changes.
#
# UI spawns this as a subprocess and listens to our stdout.  When a
# medium comes or goes we send a line to stdout describing the change;
# the UI can then choose how to react.
#
# This is in a separate process because it interacts badly with the Qt
# UI, slowing its start by as much as a minute.
#
import sys
import os
import pydbus
import signal
from gi.repository import GLib

# ignore the SIGUSR1 signal, we don't want to quit if we get this
def sigusr1_helper(*args):
    pass
signal.signal(signal.SIGUSR1, sigusr1_helper)


def stringify(enc):
    """Turn NUL-terminated array-of-int into a str"""
    return ''.join(map(chr, enc[:-1]))


# Maps a by-path symlink to its corresponding mountpoint slug (under
# /media).  This must match /etc/fstab.  The plan is to later use the
# same slug as a marker within the UI state to allow for selective
# addition/removal of books as media come and go.
# FIXME: we should probably use the slugs as keys to extract the paths
# dynamically, using findmnt.
EXTERNAL_PORT_PATHS = {
 '/dev/disk/by-path/platform-20980000.usb-usb-0:1.1:1.0-scsi-0:0:0:0-part1': 'sd-card',
 '/dev/disk/by-path/platform-20980000.usb-usb-0:1.2:1.0-scsi-0:0:0:0-part1': 'front-usb',
 '/dev/disk/by-path/platform-20980000.usb-usb-0:1.3:1.0-scsi-0:0:0:0-part1': 'back-usb',
}


# Not really a class, just limiting the scope of some variables.
class Media:
    def __init__(self):
        self.bus = pydbus.SystemBus()
        ud = self.bus.get('.UDisks2')

        ud_api = ud['org.freedesktop.DBus.ObjectManager']

        # Entries are by-path symlinks.
        self.mounted = []

        # Map UDisks2 object paths to by-path symlinks affected by them
        # coming and going.  More than one UDisks2 object may map to the
        # same symlink because we map both the partition and the
        # whole-block-device object to the symlink.
        self.obj2sym = {}

        # When True (i.e. just during synthesize_insertions()) we don't
        # trigger actions for insertions, just subscribe to updates and
        # populate mappings.
        self.synthetic = True
        self.synthesize_insertions(ud_api)
        self.synthetic = False

        # Drivers vary in their handling of removal of a medium.  Our
        # (2640) SD card reader whole-medium block device will persist
        # when the card is removed but will shrink to zero size.
        # There's no implicit unmounting of rudely removed media, so we
        # do that manually.  USB sticks' block devices disappear when
        # they're removed.  There's no implicit unmounting of rudely
        # removed media, so we do that.  So multiple subscriptions are
        # used to handle these cases.  Adding to the fun is that pydbus
        # doesn't always give all the information needed to work out
        # what to do, so there's some caching thrown in.
        ud_api.InterfacesAdded.connect(self.handle_medium_insertion)
        ud_api.InterfacesRemoved.connect(self.handle_medium_removal)

        # Simulate these either with udisksadm monitor or with:
        #   dbus-monitor --system \
        #       sender='org.freedesktop.UDisks2',\
        #       arg0='org.freedesktop.UDisks2.Filesystem',\
        #       member=PropertiesChanged,\
        #       interface=org.freedesktop.DBus.Properties
        self.bus.subscribe(sender='org.freedesktop.UDisks2',
                           iface='org.freedesktop.DBus.Properties',
                           signal='PropertiesChanged',
                           arg0='org.freedesktop.UDisks2.Filesystem',
                           signal_fired=self.handle_mounts)

        self.bus.subscribe(sender='org.freedesktop.UDisks2',
                           iface='org.freedesktop.DBus.Properties',
                           signal='PropertiesChanged',
                           arg0='org.freedesktop.UDisks2.Block',
                           signal_fired=self.handle_device_shrinks)

    def synthesize_insertions(self, ud_api):
        """Generate an insertion event for each mounted medium"""
        existing_media = ud_api.GetManagedObjects()
        for (obj, properties) in existing_media.items():
            if 'org.freedesktop.UDisks2.Filesystem' in properties:
                self.handle_medium_insertion(obj, properties)
                params = (
                    'org.freedesktop.UDisks2.Filesystem',
                    properties['org.freedesktop.UDisks2.Filesystem'],
                    []
                )
                self.handle_mounts(None, obj, None, None, params)

    def handle_medium_insertion(self, object_path, properties):
        """Handle medium insertion in external ports"""
        # Gets callback from pydbus for any new block device.
        #
        # For new media, add UDisks2 object mappings and subscribe to
        # changes in whole-block-device size.  The mount itself is
        # handled elsewhere (see constructor).
        #
        # Upon removal pydbus will only tell us the block device name
        # and what interfaces went away, not the symlinks.  So we'll
        # need to record the mapping.

        # If we're given just the Block then no FS is recognised, so
        # ignore it.  Happens with whole-disk devices.
        if 'org.freedesktop.UDisks2.Filesystem' not in properties:
            return

        # If we're not given a Block then we can't check it's an
        # external medium, so ignore it.  Haven't seen this happen.
        if 'org.freedesktop.UDisks2.Block' not in properties:
            return

        syms = properties['org.freedesktop.UDisks2.Block']['Symlinks']

        for sym in map(stringify, syms):
            if sym in EXTERNAL_PORT_PATHS:
                self.obj2sym[object_path] = sym
                fs = self.bus.get('.UDisks2', object_path)

                # Since our devices are all partitions they'll always
                # have parent devices with tables.
                table = fs['org.freedesktop.UDisks2.Partition'].Table
                self.obj2sym[table] = sym

    def handle_medium_removal(self, object_path, lost_interfaces):
        """Handle media disappearing from external ports"""
        # Pretty much all we can use is the object path.
        # We may or may not be interested in this object.
        if 'org.freedesktop.UDisks2.Block' not in lost_interfaces:
            return
        if object_path not in self.obj2sym:
            return
        sym = self.obj2sym[object_path]
        if sym in self.mounted:
            self.mounted.remove(sym)
            print('removed %s' % EXTERNAL_PORT_PATHS[sym])
            sys.stdout.flush()

    @staticmethod
    def known_mountpoint(mountpoint):
        for slug in EXTERNAL_PORT_PATHS.values():
            if mountpoint.endswith(slug):
                return True
        return False

    def handle_mounts(self, sender, obj, iface, signal, params):
        """Handle mounts of newly inserted media"""
        (ud_iface, changed, invalidated) = params
        if ud_iface != 'org.freedesktop.UDisks2.Filesystem':
            return
        if 'MountPoints' not in changed:
            return
        if len(changed['MountPoints']) != 1:
            return
        mountpoint = stringify(changed['MountPoints'][0])
        if not self.known_mountpoint(mountpoint):
            return
        sym = self.obj2sym[obj]
        assert sym not in self.mounted
        self.mounted.append(sym)
        if not self.synthetic:
            print('inserted %s' % EXTERNAL_PORT_PATHS[sym])
            sys.stdout.flush()

    def handle_device_shrinks(self, sender, obj, iface, signal, params):
        # Handle devices that shrink to zero but persist when medium is
        # removed.  We'll only get a call for the whole-medium device,
        # not the partitions.
        (ud_iface, changed, invalidated) = params
        if 'Size' not in changed:
            return
        if changed['Size'] != 0:
            return
        sym = self.obj2sym[obj]
        if sym in self.mounted:
            # OS won't do a unmount; do one ourselves, mostly so that we
            # get a proper mount notification when it comes back.
            os.system('sudo umount %s' % sym)
            self.mounted.remove(sym)
            print('removed %s' % EXTERNAL_PORT_PATHS[sym])
            sys.stdout.flush()


media = Media()
loop = GLib.MainLoop()
loop.run()
