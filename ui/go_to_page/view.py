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

    data.append(utility.format_title(
        title_text, width, page, total_pages))

    selection = state['go_to_page']['selection']
    if selection == '':
        selection = -1
    else:
        selection = int(selection) - 1

    t = utility.format_title('go to page number', width,
                             selection, total_pages, capitalize=False)
    data.append(t)

    data.append(to_braille('please confirm by pressing forward'))
    data.append(to_braille('undo by pressing back'))
    data.append(to_braille('to go back to book press middle button'))

    for _ in range(height - 6):
        data.append((0,) * width)

    return tuple(data)
