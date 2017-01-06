from functools import partial
import utility
from actions import actions
from collections import OrderedDict

menu = OrderedDict([
    ('replace library from USB stick' , partial(actions.replace_library, 'start')),
    ('shutdown'                       , actions.shutdown),
    ('backup log to USB stick'        , partial(actions.backup_log, 'start')),
    ('run warm up routine'            , partial(actions.warm_up, 'start')),
])

menu_titles_braille = map(utility.alphas_to_pin_nums, menu)
