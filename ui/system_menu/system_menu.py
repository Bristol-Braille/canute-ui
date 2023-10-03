from collections import OrderedDict
import os
import curses.ascii as ASCII

from ..braille import from_unicode, alpha_to_unicode, ueb_number_mapping
from ..state import state


def create():
    sys_menu = system_menu()
    return tuple(map(from_unicode, sys_menu))


def brailleify(rel):
    """Turn 1.3.45 or AKPR54633-1PHI into UEB"""
    # FIXME: if we do this at all it should be in braille.py, and we
    # probably shouldn't be trying to do liblouis-level translation at
    # all.
    ret = u''
    digits = False
    for c in rel:
        if ASCII.isdigit(c):
            if not digits:
                ret += u'⠼'
                digits = True
            c = ueb_number_mapping[int(c)]
            ret += alpha_to_unicode(c)
        elif c == '.':
            ret += u'⠲'
        elif ASCII.isalpha(c):
            if digits:
                # UEB 'guidelines for technical material' suggests capital
                # letter marker, not letter sign
                ret += u'⠠'
                digits = False
            ret += alpha_to_unicode(c)
        else:  # e.g. dash in serial
            digits = False
            ret += alpha_to_unicode(c)
    return ret


# This exists on a Pi and reading it yields a useful board identifier.
# But existence will do for right now.
if os.path.exists('/sys/firmware/devicetree/base/model'):
    with open('/etc/canute_release') as x:
        release = brailleify(x.read().strip())
    with open('/etc/canute_serial') as x:
        serial = brailleify(x.read().strip())
else:
    # Assume we're being emulated.
    release = brailleify(_('emulated'))
    serial = release

def do_nothing():
    pass

def system_menu():
    return OrderedDict([
        (_('shutdown'), state.app.shutdown),
        (_('backup log to USB stick'), state.app.backup_log),
        (_('select language and code'), state.app.go_to_language_menu),
        ((''), do_nothing),
        ((' '), do_nothing),
        (('  '), do_nothing),
        (_('release:') + ' ' + release, do_nothing),
        (_('serial:') + ' ' + serial, do_nothing),
    ])
