from collections import OrderedDict

from ..braille import from_unicode
from ..actions import actions


def create():
    sys_menu = system_menu()
    return tuple(map(from_unicode, sys_menu))


def system_menu():
    return OrderedDict([
        (_('shutdown'), actions.shutdown()),
        (_('backup log to USB stick'), actions.backup_log('start')),
        (_('select language'), actions.go_to_language_menu())
    ])
