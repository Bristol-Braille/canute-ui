from ..i18n import BUILTIN_LANGUAGES, install
from ..manual import Manual, manual_filename
from .. import state


class LanguageState:
    def __init__(self, root: 'state.RootState'):
        self.root = root
        self.available = BUILTIN_LANGUAGES
        self.selection = ''
        self.keys_pressed = ''

    def select_language(self, value):
        lang = abs(int(value))
        keys = list(self.available.keys())
        if lang < len(keys):
            locale = keys[lang]
            install(locale)
            manual = Manual.create()
            self.root.app.user.books[manual_filename] = manual
            self.root.app.user.current_language = locale
            self.root.app.location = 'book'
            self.root.refresh_display()
            self.root.save_state()
