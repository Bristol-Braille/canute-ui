from .. import utility

to_braille = utility.to_braille

def render(width, height, state):
    data = [to_braille('enter page number using the side buttons')]


    try:
        book = state['books'][state['book']]
    except IndexError:
        book = None

    if book is None:
        total_pages = 0
        page = 0
        title_text = 'no book'
    else:
        total_pages = utility.get_max_pages(book, height)
        page = book.page
        title_text = book.title


    if (total_pages > 9999):
        log.warning('books exceeding 9999 pages are currently not supported')

    data.append(utility.format_title(title_text, width, page, total_pages))

    selection =  state['go_to_page_selection']
    if selection == '':
        selection = 0
    else:
        selection = int(selection) + 1
    t = ('go to page number' + ' ' * 100)[0:width - (2 * 3) - 3 - 1]
    go_to = '{} {:0>3} / {:0>3}'.format(t, selection, total_pages + 1)
    data.append(to_braille(go_to))

    data.append(to_braille('please confirm by pressing forward'))
    data.append(to_braille('undo by pressing back'))
    data.append(to_braille('to go back to book press middle button'))

    for _ in range(height - 5):
        data.append((0,) * width)

    return tuple(data)
