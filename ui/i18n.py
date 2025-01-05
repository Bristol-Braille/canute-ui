import os.path
import gettext
import logging
from collections import OrderedDict
from . import config_loader
from .braille import brailleify

log = logging.getLogger(__name__)


# search external media (sd/usb1/usb2) then built-in ui dir
# for locale translation directories
def locale_dirs():
    config = config_loader.load()
    files = config.get('files', {})
    media_dir = files.get('media_dir')
    library = files.get('library', [])
    dirs = [os.path.join(media_dir, lib.get('path')) for lib in library]
    # add the default relative path for the ui installation
    dirs.append('ui')
    return dirs


def load_translations(locale_code):
    for dir in locale_dirs():
        localedir = os.path.join(dir, 'locale')
        if os.path.exists(localedir):
            try:
                return gettext.translation('canute', localedir, languages=[locale_code])
            except OSError as e:
                pass
    return None


def install(locale_code, fallback=False):
    translations = load_translations(locale_code)

    if translations is None:
        if fallback:
            log.warning(f"Unable to install language {locale_code}, using null translation")
            translations = gettext.NullTranslations()
        else:
            log.warning(f"Unable to install language {locale_code}, language left unchanged")
            return
    translations.install()
    log.info(f"installed translation language {locale_code}")
    return translations


# we don't actually want to translate the generic key below, so
# just mark it using this identity function
def _(x): return x

# TRANSLATORS: This is the title/label used for this language in the
# language menu. It should always appear in the language it denotes so
# that it remains readable to those who speak only that language.
# Addition of a Braille grade marker is appropriate, if possible.
TRANSLATION_LANGUAGE_TITLE = _('Language Name, UEB grade')

# remove the dummy _ definition ready to install the real translator
del _


DEFAULT_LOCALE = 'en_GB.UTF-8@ueb2'

translations = install(DEFAULT_LOCALE, True)
# this will've already been installed globally, but this keeps flake8 happy
_ = translations.gettext


def available_languages():
    languages = []
    for dir in locale_dirs():
        localedir = os.path.join(dir, 'locale')
        if os.path.exists(localedir):
            subfolders = [f.name for f in os.scandir(localedir) if f.is_dir()]
            for lang in subfolders:
                mofile = os.path.join(localedir, lang, 'LC_MESSAGES', 'canute.mo')
                if os.path.exists(mofile):
                    languages.append(lang)

    menu = OrderedDict()
    for lang in sorted(set(languages)):
        translation = load_translations(lang)
        if translation:
            title = translation.gettext(TRANSLATION_LANGUAGE_TITLE)
            if title == TRANSLATION_LANGUAGE_TITLE:
                title = brailleify(lang)
                log.warning(f"language file for {lang} missing '{TRANSLATION_LANGUAGE_TITLE}' title string")
            else:
                log.info(f"found language {lang} entitled {title}")
            menu[lang] = title

    return menu


# For detecting the default language of older installations, which
# didn't really have switchable language but did add a default
# sort-of-locale to the global state file.
OLD_DEFAULT_LOCALE = 'en_GB:en'
