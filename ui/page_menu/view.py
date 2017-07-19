from .. import utility

def to_braille(s):
    return utility.alphas_to_pin_nums(s)


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
        total_pages = utility.get_max_pages(book['data'], height)
        page = book['page']
        title_text = utility.get_title(book)


    if (total_pages > 9999):
        log.warning('books exceeding 9999 pages are currently not supported')


    t = (title_text + ' ' * 100)[0:width - 11] + ' '
    title = '{} {:>4}/{:>4}'.format(t, str(page), str(total_pages))
    data.append(to_braille(title))

    t = ('go to page number' + ' ' * 100)[0:width - 10]
    go_to = '{} {:>4}/{:>4}'.format(t, state['page_menu']['selection'], total_pages)
    data.append(to_braille(go_to))

    data.append(to_braille('please confirm by pressing forward'))
    data.append(to_braille('delete character by pressing back'))
    data.append(to_braille('to go back to book press middle button'))

    return tuple(data)
