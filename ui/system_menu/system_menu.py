from collections import OrderedDict

from ..braille import from_ascii
from ..actions import actions
from ..i18n import I18n


def create(locale='en_GB:en'):
    i18n = I18n(locale)
    sys_menu = system_menu(i18n)
    return tuple(map(from_ascii, sys_menu))

def system_menu(i18n=I18n()):
    return OrderedDict([
        (i18n._('shutdown'), actions.shutdown()),
        (i18n._('backup log to USB stick'), actions.backup_log('start')),
        (i18n._('select language'), actions.go_to_language_menu())
    ])
