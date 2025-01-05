import os.path
import gettext
import logging
from collections import OrderedDict
from . import config_loader

log = logging.getLogger(__name__)


# search external media (sd/usb1/usb2) then built-in ui dir
# for locale translation directories
def locale_dirs():
    config = config_loader.load()
    dirs = [lib['path'] for lib in config.get('files', {}).get('library', [])]
    dirs.append('ui')
    return dirs


def install(locale_code, fallback=False):
    translations = None
    for dir in locale_dirs():
        localedir = os.path.join(dir, 'locale')
        if os.path.exists(localedir):
            try:
                translations = gettext.translation(
                    'canute', localedir, languages=[locale_code]
                )
                break
            except OSError as e:
                log.warning(e)
                pass

    if translations is None:
        if fallback:
            translations = gettext.NullTranslations()
        else:
            log.warning(f"Unable to install language {locale_code}, language left unchanged")
            return
    translations.install()
    log.info(f"installed translation language {locale_code}")
    return translations

DEFAULT_LOCALE = 'en_GB.UTF-8@ueb2'

translations = install(DEFAULT_LOCALE, True)
# this will've already been installed globally, but this keeps flake8 happy
_ = translations.gettext

# TRANSLATORS: This is the title/label used for this language in the
# language menu. It should always appear in the language it denotes so
# that it remains readable to those who speak only that language.
# Addition of a Braille grade marker is appropriate, if possible.
TRANSLATION_LANGUAGE_TITLE = _('Language Name, UEB grade')

def available_languages():
    languages = []
    for dir in locale_dirs():
        localedir = os.path.join(dir, 'locale')
        if os.path.exists(localedir):
            subfolders = [ f.name for f in os.scandir(localedir) if f.is_dir() ]
            for lang in subfolders:
                mofile = os.path.join(localedir, lang, 'LC_MESSAGES', 'canute.mo')
                if os.path.exists(mofile):
                    languages.append(lang)

    menu = OrderedDict()
    for lang in set(languages):
        translation = gettext.translation(lang)
        title = translation.gettext(TRANSLATION_LANGUAGE_TITLE, lang)
        menu[lang] = title

    return menu

# For detecting the default language of older installations, which
# didn't really have switchable language but did add a default
# sort-of-locale to the global state file.
OLD_DEFAULT_LOCALE = 'en_GB:en'
