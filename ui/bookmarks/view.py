from .. import utility

to_braille = utility.to_braille


def render(width, height, state):
    book = state['books'][state['book']]
    page = state['bookmarks_menu']['page']
    bookmarks = book.bookmarks[page * height:(page * height) + height]
    data = []
    for page in bookmarks:
        if page == 'deleted':
            data += ((0,) * width,)
            continue
        line = book[page * height:(page * height) + 1][0]
        data.append(tuple(utility.to_braille(str(page + 1))) + (0,) + line)

    # pad page with empty rows
    while len(data) < height:
        data += ((0,) * width,)

    return tuple(data)
