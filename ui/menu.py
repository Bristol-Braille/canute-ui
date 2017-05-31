from functools import partial
import utility
from actions import actions
from collections import OrderedDict

menu = OrderedDict([
    (
        'replace library from USB stick',
        partial(actions.replace_library, 'start')
    ),
    ('shutdown', actions.shutdown),
    ('backup log to USB stick', partial(actions.backup_log, 'start')),
    ('reset display', partial(actions.reset_display, 'start')),
    ('update UI from USB stick', partial(actions.update_ui, 'start')),
])

menu_titles_braille = map(utility.alphas_to_pin_nums, menu)
