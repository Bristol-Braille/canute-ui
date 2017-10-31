import asyncio
from ..actions import actions
from .. import utility


def queue_key_press(key):
    @asyncio.coroutine
    def thunk(dispatch, get_state):
        state = get_state()['app']

        selection = state['go_to_page']['selection']
        keys_pressed = state['go_to_page']['keys_pressed']

        # ignore any initial zero presses or deletes
        if (key == 0 or key == '<') and selection + keys_pressed == '':
            return

        yield from dispatch(actions.go_to_page_key_press(key))

        num_width = utility.get_page_num_width(state)
        if len(keys_pressed) < num_width:
            yield from asyncio.sleep(0.5)

        keys_pressed = get_state()['app']['go_to_page']['keys_pressed']
        if keys_pressed != '':
            yield from dispatch(actions.go_to_page_set_selection())

    return thunk


go_to_page_buttons = {
    'single': {
        'L': actions.close_menu(),
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
        '>': actions.go_to_page_confirm(),
        'R': actions.toggle_help_menu(),
    },
    'long': {
        'L': actions.close_menu(),
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
        '>': actions.go_to_page_confirm(),
        'R': actions.toggle_help_menu(),
    },
}
