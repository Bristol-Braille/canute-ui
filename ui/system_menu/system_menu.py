from collections import OrderedDict
import curses.ascii as ASCII
import os

from ..braille import from_unicode, alpha_to_unicode, ueb_number_mapping
from ..actions import actions


def create():
    sys_menu = system_menu()
    return tuple(map(from_unicode, sys_menu))


def brailleify(rel):
    '''Turn 1.3.45 or AKPR54633-1PHI into UEB'''
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


with open('/etc/canute_release') as x:
    release = brailleify(x.read().strip())
serial = brailleify(os.popen('/home/pi/util/getserial.py').read().strip())


def system_menu():
    return OrderedDict([
        (_('shutdown'), actions.shutdown()),
        (_('backup log to USB stick'), actions.backup_log('start')),
        (_('select language and code'), actions.go_to_language_menu()),
        ((''), actions.do_nothing()),
        ((' '), actions.do_nothing()),
        (('  '), actions.do_nothing()),
        (_('release:') + ' ' + release, actions.do_nothing()),
        (_('serial:') + ' ' + serial, actions.do_nothing()),
    ])
