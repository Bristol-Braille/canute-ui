from ..manual import Manual, manual_filename


class LanguageReducers():
    def select_language(self, state, value):
        languages = state['languages']
        lang = abs(int(value))
        keys = list(languages['available'].keys())
        locale = keys[lang] if lang < len(keys) else 'en_GB:en'
        manual = Manual.create(locale)
        books = state['user']['books'].copy(**{manual_filename: manual})
        user = state['user'].copy(current_language=locale, books=books)
        return state.copy(location='book', user=user)