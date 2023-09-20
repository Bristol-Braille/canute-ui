from ..i18n import BUILTIN_LANGUAGES, install
from ..manual import Manual

class LanguageState:
    def __init__(self, root):
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
            self.root.user.books.set('manual_filename', manual)
            self.root.user.current_language = locale
            self.root.location = 'book'
            # trigger redraw
