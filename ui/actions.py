action_types = [
    'set_books',
    'go_to_book',
    'go_to_library',
    'go_to_menu',
    'next_page',
    'previous_page',
    'replace_library',
    'shutdown',
    'backup_log',
]


def make_action_method(name):
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))


