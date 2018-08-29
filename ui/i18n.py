import gettext
import logging


log = logging.getLogger(__name__)


class I18n:
    def __init__(self, locale='en_GB:en'):
        self.lang = locale

    def _(self, key):
        try:
            language = self.lang
            translate = gettext.translation(
                'canute', localedir='ui/locale', languages=[language], fallback=False)
            translate.install()
        except Exception as e:
            log.warning(e)
            translate = gettext.NullTranslations()
        return translate.gettext(key)
