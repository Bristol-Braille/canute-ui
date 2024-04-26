from ..state import state
from . import upgrade

def install_upgrade():
    if upgrade.available:
        upgrade.upgrade()

buttons = {
    'single': {
        '2': state.app.shutdown,
        '3': state.app.go_to_language_menu,
        '4': install_upgrade,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
    },
    'long': {
        '2': state.app.shutdown,
        '3': state.app.go_to_language_menu,
        '4': install_upgrade,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
        'X': state.hardware.reset_display,
    },
}
