from functools import partial
import logging
log = logging.getLogger(__name__)

import utility
import menu
from button_bindings import button_bindings


initial_state = {
    'location'        : 'library',
    'library'         : {'data': tuple(), 'page': 0},
    'menu'            : {
        'data': map(partial(utility.pad_line, 40), menu.menu_titles_braille),
        'page': 0
    },
    'books'           : tuple(),
    'replace_library' : False,
    'button_bindings' : button_bindings,
    'display'         : {'width': 40, 'height': 9}
}
