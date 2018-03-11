from collections import OrderedDict

from ..braille import from_ascii
from ..actions import actions

system_menu = OrderedDict([
    ('shutdown', actions.shutdown()),
])

menu_titles = tuple(map(from_ascii, system_menu))
