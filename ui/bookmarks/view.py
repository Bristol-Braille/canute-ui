from ..braille import to_braille, format_title


def render_help_menu(width, height):
    data = []

    data.append(to_braille('Add a bookmark by pressing button 5'))
    data.append(to_braille('while in a book. Bookmarks are listed'))
    data.append(to_braille('here in the bookmark menu. Each bookmark'))
    data.append(to_braille('starts with the Canute page number based'))
    data.append(to_braille('on its 9 line page. Go to the page by'))
    data.append(to_braille('selecting a bookmark by pressing one of'))
    data.append(to_braille('the side buttons. Holding the button'))
    data.append(to_braille('down will delete the bookmark.'))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)


async def render(width, height, state, store):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height)

    book = state['books'][state['book']]
    page = state['bookmarks_menu']['page']

    line_n = page * (height - 1)
    bookmarks = book.bookmarks[line_n:line_n + (height - 1)]

    max_pages = (len(book.bookmarks) - 1) // (height - 1)
    title = format_title(
        'bookmarks: {}'.format(book.title),
        width, page, max_pages)
    data = [title]

    for bm in bookmarks:
        if bm == 'deleted':
            data.append(tuple())
            continue
        lines = await book.current_page_text(store)
        line = lines[0]
        data.append(tuple(to_braille(str(bm + 1))) + (0,) + tuple(line))

    # pad page with empty rows
    while len(data) < height:
        data.append(tuple())

    return tuple(data)
