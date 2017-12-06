from ..braille import from_ascii, format_title


def render_help_menu(width, height, page):
    data = [
        'Go to a page number by keying it in with',
        'the side number buttons and pressing',
        'forward. Pages are numbered based on the',
        '9 line page height of the Canute. You',
        'can delete entered numbers by pressing',
        'or holding the back button. As always'
        'you can go back to your current page by',
        'pressing the menu button.',
    ]

    data = [from_ascii(line) for line in data]

    while len(data) < height:
        data.append(tuple())

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'])

    data = [from_ascii('enter page number using the side buttons')]

    try:
        book = state['user']['books'][state['user']['book']]
    except IndexError:
        book = None

    if book is None:
        total_pages = 0
        page = 0
        title_text = 'no book'
    else:
        total_pages = book.max_pages
        page = book.page_number
        title_text = book.title

    data.append(format_title(
        title_text, width, page, total_pages))

    selection = state['go_to_page']['selection']
    if selection == '':
        selection = -1
    else:
        selection = int(selection) - 1

    t = format_title('go to page number', width,
                     selection, total_pages, capitalize=False)
    data.append(t)

    data.append(from_ascii('please confirm by pressing forward'))
    data.append(from_ascii('undo by pressing back'))
    data.append(from_ascii('to go back to book press middle button'))

    for _ in range(height - 6):
        data.append(tuple())

    return tuple(data)
