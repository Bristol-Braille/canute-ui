from ..braille import format_title, from_unicode


def render_help(width, height):
    data = []
    para = _('''\
To navigate to a page within a file, enter the page number using the \
line select buttons on the left hand side of Canute 360. For example, \
for page 10, press button 1 followed by button 0.  Press the forward \
button to confirm your selection. Line 3 will refresh to show your \
selected page. Press the forward button to navigate to your page.  If \
you have entered the wrong page number, press the back button to reset \
the selection on line 3. You can then enter the correct number using \
the line select keys, before pressing forward to confirm, and pressing \
forward once more to navigate to the selected page.''')

    for line in para.split('\n'):
        data.append(from_unicode(line))

    while len(data) % height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        all_lines = render_help(width, height)
        num_pages = len(all_lines) // height
        page_num = min(state['help_menu']['page'], num_pages - 1)
        first_line = page_num * height
        off_end = first_line + height
        page = all_lines[first_line:off_end]
        return page

    data = [from_unicode(_('enter page number using the side buttons'))]

    try:
        book = state['user']['books'][state['user']['current_book']]
    except IndexError:
        book = None

    if book is None:
        total_pages = 0
        page = 0
        title_text = 'no book'
    else:
        total_pages = len(book.pages)
        page = book.page_number
        title_text = book.title

    data.append(format_title(
        title_text, width, page, total_pages))

    selection = state['go_to_page']['selection']
    if selection == '':
        selection = -1
    else:
        selection = int(selection) - 1

    t = format_title(_('go to page number'), width,
                     selection, total_pages, capitalize=False)
    data.append(t)

    data.append(from_unicode(_('please confirm by pressing forward')))
    data.append(from_unicode(_('undo by pressing back')))
    data.append(from_unicode(_('to go back to book press middle button')))

    for __ in range(height - 6):
        data.append(tuple())

    return tuple(data)
