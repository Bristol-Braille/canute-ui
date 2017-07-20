import asyncio
from ..actions import actions
from .. import utility

n = ''

def enter_number(num):
    @asyncio.coroutine
    def thunk(dispatch, get_state):
        state = get_state()['app']

        selection = state['go_to_page']['selection']
        keys_pressed = state['go_to_page']['keys_pressed']

        #ignore any initial zero presses
        if num == 0 and selection + keys_pressed == '':
            return

        yield from dispatch(actions.go_to_page_key_press(num))

        num_width = utility.get_page_num_width(state)

        if len(keys_pressed) < num_width:
            yield from asyncio.sleep(0.8)

        keys_pressed = get_state()['app']['go_to_page']['keys_pressed']
        if keys_pressed != '':
            yield from dispatch(actions.go_to_page_set_selection())

    return thunk


go_to_page_buttons = {
    'single': {
        'L': actions.close_menu(),
        '1': enter_number(1),
        '2': enter_number(2),
        '3': enter_number(3),
        '4': enter_number(4),
        '5': enter_number(5),
        '6': enter_number(6),
        '7': enter_number(7),
        '8': enter_number(8),
        '9': enter_number(9),
        'X': enter_number(0),
        '<': actions.go_to_page_delete(),
        '>': actions.go_to_page_confirm(),
        'R': actions.reset_display('start'),
    },
}
