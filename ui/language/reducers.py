import re
from .. import utility


class LanguageReducers():
    def select_language(self, state, value):
        languages = state['languages']
        lang = value
        locale = list(languages['available'].keys())[lang]
        user = state['user'].copy(current_language=locale)
        print(user['current_language'])
        return state.copy(location='book', user=user)