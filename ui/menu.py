from functools import partial
import utility
from actions import actions

menu = {
    'replace library from USB stick' : partial(actions.replace_library, True),
    'shutdown'                       : actions.shutdown,
    'backup log to USB stick'        : actions.backup_log,
}

menu_titles_braille = map(utility.alphas_to_pin_nums, menu)
