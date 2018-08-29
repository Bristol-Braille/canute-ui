import locale
import gettext


current_locale, encoding = locale.getdefaultlocale()

locale_path = 'ui/locale/'
language = gettext.translation('canute', locale_path, [current_locale])
language.install()
