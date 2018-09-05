from ..braille import from_ascii, format_title, to_ueb_number
from ..i18n import I18n


def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = []
    para = from_ascii(i18n._('''\
Select a language by using the side
number buttons and pressing forward.'''))

    lines = para.split('\n')

    for line in lines:
        data.append(line)

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height, state['user'].get('current_language', 'en_GB:en'))

    lang = state['user'].get('current_language', None)
    languages = state['languages']['available']
    current_lang = languages.get(lang, 'English')

    try:
        cur_index = list(languages.keys()).index(lang)
    except ValueError:
        cur_index = -1

    title = format_title(
        'languages: {}'.format(current_lang),
        width, cur_index, len(languages.keys()))
    data = [title]

    for lang in languages:
        langs = list(languages.keys()).index(lang)
        n = from_ascii(to_ueb_number(langs + 1) + ' ')
        data.append(n + tuple(from_ascii(languages[lang])))

    while len(data) < height:
        data.append(tuple())

    return tuple(data)
