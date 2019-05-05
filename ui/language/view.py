from ..braille import from_ascii, format_title, to_ueb_number, from_unicode


def render_help(width, height):
    data = []
    para = _('''\
You can change the system language or Braille code (for example to \
switch between contracted and un-contracted Braille) from the system \
menu.  Please note this will only change the language and code within \
the menus, help file, and manuals; not the language or code in any books \
on Canute.  To access the system menu, first access the main menu by \
pressing the largest control button in the centre of the front edge of \
Canute 360.  Then, press the line select button immediately to the left \
of "VIEW SYSTEM MENU" to access the system menu.  Press the line select \
button immediately to the left of "SELECT LANGUAGE" to access the \
language selection menu. You can then select a language or Braille code \
using the triangular line select button immediately to the left of your \
chosen language or code.''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    help_menu = state['help_menu']['visible']
    if help_menu:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    lang = state['user'].get('current_language', None)
    languages = state['languages']['available']
    current_lang = languages.get(lang, 'English Grade 1')

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
