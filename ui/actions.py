import utility

class Reducers(object):
    def set_books(state):
        pass
    def go_to_book(state):
        pass
    def go_to_library(state):
        pass
    def go_to_menu(state):
        pass
    def next_page(state):
        pass
    def previous_page(state):
        pass
    def replace_library(state):
        pass
    def shutdown(state):
        pass
    def backup_log(state):
        pass

action_types = utility.get_methods(Reducers)

def make_action_method(name):
    def action_method(value = None):
        return {'type': name, 'value': value}
    return action_method


#just an empty object
def actions(): pass
#then we give it a method for each action
for action in action_types:
    setattr(actions, action, make_action_method(action))
