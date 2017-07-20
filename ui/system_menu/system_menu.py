from collections import OrderedDict

from .. import utility
from ..actions import actions

system_menu = OrderedDict([
    (
        'replace library from USB stick',
        lambda: actions.replace_library('start')
    ),
    ('shutdown', actions.shutdown),
    ('backup log to USB stick', lambda: actions.backup_log('start')),
    ('reset display', lambda: actions.reset_display('start')),
    ('update UI from USB stick', lambda: actions.update_ui('start')),
])

menu_titles = list(map(utility.to_braille, system_menu))
