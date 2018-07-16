from collections import OrderedDict

from ..braille import from_ascii
from ..actions import actions
from ..i18n import I18n

i18n = I18n()

system_menu = OrderedDict([
    (i18n._('shutdown'), actions.shutdown()),
    (i18n._('backup log to USB stick'), actions.backup_log('start')),
])

menu_titles = tuple(map(from_ascii, system_menu))
