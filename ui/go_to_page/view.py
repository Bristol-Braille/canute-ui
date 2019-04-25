from ..braille import format_title, from_unicode


def render_help(width, height):
    data = []
    para = _('''\
Go to a page number by keying it in with
the side number buttons and pressing
forward. Pages are numbered based on the
#i line page height of the Canute. You
can delete entered numbers by pressing
or holding the back button. As always
you can go back to your current page by
pressing the menu button.''')

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
