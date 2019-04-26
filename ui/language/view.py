from ..braille import from_ascii, format_title, to_ueb_number


def render_help(width, height):
    data = []
    para = _('''\
Select a language by using the side
number buttons and pressing forward.''')

    for line in para.split('\n'):
        data.append(from_ascii(line))

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help(width, height)

    lang = state['user'].get('current_language', None)
    languages = state['languages']['available']
    current_lang = languages.get(lang, 'English Grade 1')

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
