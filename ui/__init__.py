import locale
import gettext
import os

current_locale, encoding = locale.getdefaultlocale()

locale_path = 'ui/locale/'
language = gettext.translation ('canute', locale_path, [current_locale] )
language.install()