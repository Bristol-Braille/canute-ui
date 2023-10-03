import asyncio
from ..state import state
from .. import state_helpers


def queue_key_press(key):
    async def thunk(dispatch, get_state):
        selection = state.app.go_to_page_menu.selection
        keys_pressed = state.app.go_to_page_menu.keys_pressed

        # ignore any initial zero presses or deletes
        if (key == 0 or key == '<') and selection + keys_pressed == '':
            return

        state.app.go_to_page_menu.go_to_page_key_press(key)

        num_width = state_helpers.get_page_num_width(state)
        if len(keys_pressed) < num_width:
            await asyncio.sleep(0.5)

        keys_pressed = state.app.go_to_page_menu.keys_pressed
        if keys_pressed != '':
            state.app.go_to_page_menu.go_to_page_set_selection()

    return thunk


go_to_page_buttons = {
    'single': {
        'L': state.app.close_menu,
        '1': queue_key_press(1),
        '2': queue_key_press(2),
        '3': queue_key_press(3),
        '4': queue_key_press(4),
        '5': queue_key_press(5),
        '6': queue_key_press(6),
        '7': queue_key_press(7),
        '8': queue_key_press(8),
        '9': queue_key_press(9),
        'X': queue_key_press(0),
        '<': queue_key_press('<'),
        '>': state.app.go_to_page_menu.go_to_page_confirm,
        'R': state.app.help_menu.toggle,
    },
    'long': {
        'L': state.app.close_menu,
        '1': queue_key_press(1),
        '2': queue_key_press(2),
        '3': queue_key_press(3),
        '4': queue_key_press(4),
        '5': queue_key_press(5),
        '6': queue_key_press(6),
        '7': queue_key_press(7),
        '8': queue_key_press(8),
        '9': queue_key_press(9),
        'X': queue_key_press(0),
        '<': queue_key_press('<'),
        '>': state.app.go_to_page_menu.go_to_page_confirm,
        'R': state.app.help_menu.toggle,
    },
}
