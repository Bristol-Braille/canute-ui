from collections import OrderedDict

from .. import utility
from ..actions import actions

system_menu = OrderedDict([
    (
        'replace library from USB stick',
        actions.replace_library('start')
    ),
    ('shutdown', actions.shutdown()),
    ('backup log to USB stick', actions.backup_log('start')),
    ('reset display', actions.reset_display('start')),
    ('update UI from USB stick', actions.update_ui('start')),
])

menu_titles = list(map(utility.to_braille, system_menu))
print(menu_titles)
