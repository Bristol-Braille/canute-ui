from collections import OrderedDict

from ..braille import from_ascii
from ..actions import actions

system_menu = OrderedDict([
    ('shutdown', actions.shutdown()),
    ('backup log to USB stick', actions.backup_log('start')),
])

menu_titles = tuple(map(from_ascii, system_menu))
