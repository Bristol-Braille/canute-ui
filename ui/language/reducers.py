from ..manual import Manual, manual_filename
from ..i18n import install


class LanguageReducers():
    def select_language(self, state, value):
        languages = state['languages']
        lang = abs(int(value))
        keys = list(languages['available'].keys())
        if lang < len(keys):
            locale = keys[lang]
            install(locale)
            manual = Manual.create()
            books = state['user']['books'].set('manual_filename', manual)
            user = state['user'].set('current_language', locale)
            user = user.set('books', books)
            new_state = state.set('location', 'book')
            return new_state.set('user', user)
        else:
            return state
