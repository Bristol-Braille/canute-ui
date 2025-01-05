from ..braille import from_ascii, format_title, to_ueb_number, from_unicode


def render_help(width, height):
    data = []
    para = _('''\
You can change the system language or Braille code by pressing the \
line select button to the left of your chosen language or code. The \
language or code in the contextual help, menus and system text will \
then change to your selected language.\
''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state):
    help_menu = state.app.help_menu.visible
    if help_menu:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state.app.help_menu.page, num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    lang = state.app.user.current_language
    languages = state.app.languages.available
    current_lang = languages.get(lang, 'English, UEB Grade 2')

    try:
        cur_index = list(languages.keys()).index(lang)
    except ValueError:
        cur_index = -1

    # TRANSLATORS: A menu title, to which language title is appended
    title = _('languages:') + ' {}'
    title = format_title(
        title.format(current_lang),
        width, cur_index, len(languages.keys()))
    data = [title]

    for lang in languages:
        langs = list(languages.keys()).index(lang)
        n = from_ascii(to_ueb_number(langs + 1) + ' ')
        data.append(n + tuple(from_unicode(languages[lang])))

    while len(data) < height:
        data.append(tuple())

    return tuple(data)
