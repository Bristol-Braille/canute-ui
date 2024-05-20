import gettext
import logging
from collections import namedtuple, OrderedDict

log = logging.getLogger(__name__)


def install(locale_code):
    try:
        translations = gettext.translation(
            'canute', localedir='ui/locale', languages=[locale_code],
            fallback=False
        )
    except OSError as e:
        log.warning(e)
        translations = gettext.NullTranslations()
    translations.install()
    return translations


# Before having installed _() we need extractors to see language titles.
# It's convenient to have it act as the identity function, too.
def _(x): return x


Builtin = namedtuple('BuiltinLang', ['code', 'title'])

# Would prefer "British English, UEB grade N" for the following but
# (1) it's too long to be included in the languages menu title, (2) it
# might be irrelevant if there are no British-isms in this small
# collection of text, (3) US users might object on principle.

# TRANSLATORS: This is a language name menu item, so should always appear
# in the language it denotes so that it remains readable to those who
# speak only that language, just as "Deutsch" should always be left as
# "Deutsch" in a language menu.  Addition of a Braille grade marker seems
# appropriate, if possible.
builtin = [
    Builtin(code='en_GB.UTF-8@ueb1', title=_('English, UEB grade 1')),
    Builtin(code='en_GB.UTF-8@ueb2', title=_('English, UEB grade 2')),
    Builtin(code='de_DE.UTF-8@ueb1', title=_('Deutsch, UEB grade 1')),
    Builtin(code='de_DE.UTF-8@ueb2', title=_('Deutsch, UEB grade 2'))
]

del _

DEFAULT_LOCALE = 'en_GB.UTF-8@ueb2'

BUILTIN_LANGUAGES = OrderedDict([
    (lang.code, _(lang.title)) for lang in builtin
])

translations = install(BUILTIN_LANGUAGES[DEFAULT_LOCALE])

# this will've already been installed globally, but this keeps flake8 happy
_ = translations.gettext

# For detecting the default language of older installations, which
# didn't really have switchable language but did add a default
# sort-of-locale to the global state file.
OLD_DEFAULT_LOCALE = 'en_GB:en'
