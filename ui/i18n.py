import gettext
import os

# update language with 'os.environ["LANGUAGE"] = "de_DE"'

class I18n:
    def __init__(self):
        self.env_lang = None
        self.lang = None
        self.translate = None

    def _(self, key):
        print(env_lang)
        if env_lang and self.lang != env_lang:
            self.lang = env_lang
            try:
                language = self.lang
                translate = gettext.translation(
                    'canute', localedir='ui/locale', languages=[language], fallback=False)
                translate.install()
            except:
                translate = gettext.NullTranslations()
            self.translate = translate
        elif not self.translate:
            self.translate = gettext.NullTranslations()
        return self.translate.gettext(key)