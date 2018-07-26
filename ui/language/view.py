from ..braille import from_ascii, format_title, to_ueb_number
from ..i18n import I18n

def render_help_menu(width, height, page, locale):
    i18n = I18n(locale)
    data = (
        from_ascii(i18n._('Select a language by using the side')),
        from_ascii(i18n._('number buttons and pressing forward.')),
    )

    data = [from_ascii(line) for line in data]

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

    for x in languages:
        l = list(languages.keys()).index(x)
        n = from_ascii(to_ueb_number(l + 1) + ' ')
        data.append(n + tuple(from_ascii(languages[x])))

    while len(data) < height:
        data.append(tuple())

    return tuple(data)