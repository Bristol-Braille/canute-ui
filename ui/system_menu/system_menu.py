from functools import partial
from collections import OrderedDict

from .. import utility
from ..actions import actions

system_menu = OrderedDict([
    (
        'replace library from USB stick',
        partial(actions.replace_library, 'start')
    ),
    ('shutdown', actions.shutdown),
    ('backup log to USB stick', partial(actions.backup_log, 'start')),
    ('reset display', partial(actions.reset_display, 'start')),
    ('update UI from USB stick', partial(actions.update_ui, 'start')),
])

menu_titles = list(map(utility.to_braille, system_menu))
print(menu_titles)
