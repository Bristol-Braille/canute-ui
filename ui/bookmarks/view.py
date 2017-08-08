from .. import utility

to_braille = utility.to_braille


def render(width, height, state):
    book = state['books'][state['book']]
    page = state['bookmarks_menu']['page']

    line_n = page * (height - 1)
    bookmarks = book.bookmarks[line_n:line_n + (height - 1)]

    max_pages = utility.get_max_pages(book.bookmarks, height - 1)
    title = utility.format_title(
        'bookmarks: {}'.format(book.title),
        width, page + 1, max_pages + 1)
    data = [title]

    for bm in bookmarks:
        if bm == 'deleted':
            data.append((0,) * width)
            continue
        line = book[bm * height:(bm * height) + 1][0]
        data.append(tuple(to_braille(str(bm + 1))) + (0,) + line)

    # pad page with empty rows
    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)
