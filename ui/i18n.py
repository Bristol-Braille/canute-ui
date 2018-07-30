import gettext
import logging


log = logging.getLogger(__name__)


class I18n:
    def __init__(self, locale='en_GB:en'):
        if locale:
            self.lang = locale
        else:
            self.lang = None
        self.translate = None

    def _(self, key):
        if self.lang is not None:
            try:
                language = self.lang
                translate = gettext.translation(
                    'canute', localedir='ui/locale', languages=[language], fallback=False)
                translate.install()
            except Exception as e:
                log.warning(e)
                translate = gettext.NullTranslations()
            self.translate = translate
        elif not self.translate:
            self.translate = gettext.NullTranslations()
        return self.translate.gettext(key)
