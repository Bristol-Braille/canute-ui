#!/usr/bin/python3
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
import threading
import pydbus
from gi.repository import GLib

def stringify(enc):
    """Turn NUL-terminated array-of-int into a str"""
    return "".join(map(chr, enc[:-1]))

# Maps a by-path symlink to its corresponding mountpoint slug (under
# /media).  This must match /etc/fstab.  The plan is to later use the
# same slug as a marker within the UI state to allow for selective
# addition/removal of books as media come and go.
EXTERNAL_PORT_PATHS = {
 "/dev/disk/by-path/platform-20980000.usb-usb-0:1.1:1.0-scsi-0:0:0:0-part1": "sd-card",
 "/dev/disk/by-path/platform-20980000.usb-usb-0:1.2:1.0-scsi-0:0:0:0-part1": "front-usb",
 "/dev/disk/by-path/platform-20980000.usb-usb-0:1.3:1.0-scsi-0:0:0:0-part1": "back-usb",
}


# Not really a class, just limiting the scope of some variables.
class Media:
    def __init__(self):
        self.bus = pydbus.SystemBus()
        ud = self.bus.get(".UDisks2")

        ud_api = ud['org.freedesktop.DBus.ObjectManager']

        # Remember Filesystem objects whose PropertiesChanged events
        # we've subscribed to.  Entries are symlink -> pydbus
        # subscription.  For now we never use the subscription; presence
        # in here is the entire meaning.
        self.sym2sub = {}

        # Remember which UDisks2 name refers to which recognised by-path
        # symlink.  Notifications about disappearances tell us only the
        # UDisks2 name.  Entries are UDisks2 path -> symlink.
        self.obj2sym = {}

        # When True (i.e. just during synthesize_insertions()) we don't
        # trigger actions for insertions, just subscribe to updates and
        # populate mappings.
        self.synthetic = True
        self.synthesize_insertions(ud_api)
        self.synthetic = False

        ud_api.InterfacesAdded.connect(self.handle_media_changes)
        ud_api.InterfacesRemoved.connect(self.handle_medium_removal)


    def synthesize_insertions(self, ud_api):
        """Generate an insertion event for each existing medium"""
        existing_media = ud_api.GetManagedObjects()
        for (obj, properties) in existing_media.items():
            self.handle_media_changes(obj, properties)

    # Should probably be handle_medium_insertion() ?
    def handle_media_changes(self, object_path, properties):
        """Handle media coming and going in external ports"""
        # This gets called by pydbus for any new block device.
        #
        # For new media, subscribe to see mount (probably in a few
	# milliseconds' time).  For now, when we see the mount, notify
	# the UI main loop which will restart the UI.  We could handle
	# this with more finesse later, adding books with a property
	# denoting the medium they reside on, and rebuilding the menu.
        #
	# For removed media, again notify the UI main loop which will
	# restart the UI.  We could handle this with more finesse later,
	# removing only the books on this medium and then rebuilding the
	# menu.  Technically we should also cancel subscriptions to
	# PropertiesChanged on the disappearing medium, but in practice
	# this doesn't seem to be necessary; old subs seem to continue
	# working when the port gets used again.
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

        # Few decent ways exist to have callback know which medium was
        # mounted.  A closure seems least bad.
        def handle_mount_changes(iface, changed, invalidated):
           """Handle mounts/unmounts of removeable media"""
           # FIXME do we need to handle brute-force unmounts?  I don't
           # fancy yanking a block device under braille VM because Qubes
           # bugs.  But I don't know whether we get notifications.  If
           # we get both, things are nice and symmetrical.  If we don't
           # get mount-yank notifications, it's muddier.
           assert(iface == 'org.freedesktop.UDisks2.Filesystem')
           if 'MountPoints' not in changed:
               return
           # If a medium gets yanked we'll catch it at the block level,
           # but we allow for a notification here with MountPoints
           # empty.
           if len(changed['MountPoints']) != 1:
               return
           if not self.synthetic:
               sym = self.obj2sym[object_path]
               print("inserted %s" % EXTERNAL_PORT_PATHS[sym])

        for sym in map(stringify, syms):
            if sym in EXTERNAL_PORT_PATHS and sym not in self.sym2sub:
                fs = self.bus.get(".UDisks2", object_path)
                # Only FS property changes are interesting.
                fs = fs['org.freedesktop.UDisks2.Filesystem']
                self.sym2sub[sym] = fs.PropertiesChanged.connect(handle_mount_changes)

    def handle_medium_removal(self, object_path, lost_interfaces):
        """Handle media disappearing from external ports"""
        if not self.synthetic:
            sym = self.obj2sym[object_path]
            print("removed %s" % EXTERNAL_PORT_PATHS[sym])

media = Media()
loop = GLib.MainLoop()
loop.run()
