import os
from ..state import state
from . import upgrade
from .system import console

def exit_to_console():
    if console:
        os.system('sudo systemctl start brltty@canute.path')

def install_upgrade():
    if upgrade.available:
        upgrade.upgrade()


buttons = {
    'single': {
        '2': exit_to_console,
        '3': state.app.shutdown,
        '4': state.app.go_to_encoding_menu,
        '5': state.app.go_to_language_menu,
        '6': state.backup_log,
        '7': install_upgrade,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
    },
    'long': {
        '2': exit_to_console,
        '3': state.app.shutdown,
        '4': state.app.go_to_encoding_menu,
        '5': state.app.go_to_language_menu,
        '6': state.backup_log,
        '7': install_upgrade,
        'R': state.app.help_menu.toggle,
        '>': state.app.next_page,
        '<': state.app.previous_page,
        'L': state.app.close_menu,
        'X': state.hardware.reset_display,
    },
}
