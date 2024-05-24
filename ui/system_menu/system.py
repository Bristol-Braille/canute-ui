import os
from ..config_loader import load
from ..braille import brailleify

console = load().get('system', {}).get('console', False)
release = _('release:') + ' '
serial = _('serial:') + ' '

if console:
    # TRANSLATORS: This message is first line of a two line
    # message shown in place of the release and serial number
    # when the Canute 360 is connected to the console
    release = _('Unplug from Console for release')
    # TRANSLATORS: This is the second line of the two line
    # message shown when connected to the console
    serial = _('and serial numbers')

# This exists on a Pi and reading it yields a useful board identifier.
# But existence will do for right now.
elif os.path.exists('/sys/firmware/devicetree/base/model'):
    if os.path.exists('/etc/canute_release'):
        with open('/etc/canute_release') as x:
            release += brailleify(x.read().strip())
        with open('/etc/canute_serial') as x:
            serial += brailleify(x.read().strip())

# Otherwise assume we're being emulated.
else:
    emulated = _('emulated')
    release += emulated
    serial += emulated
