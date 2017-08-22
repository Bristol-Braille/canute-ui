from .. import utility

to_braille = utility.to_braille


def render_home_menu(width, height, book):
    data = []
    max_pages = utility.get_max_pages(book, height)
    data.append(utility.format_title(
        book.title, width, book.page, max_pages))
    data.append(to_braille('go to page'))
    data.append(to_braille('go to start of book'))
    data.append(to_braille('go to end of book'))
    data.append(to_braille('insert bookmark at current page'))
    data.append(to_braille('choose from existing bookmarks'))
    data.append((0,) * width)
    data.append(to_braille('view system menu'))
    data.append(to_braille('view library menu'))
    return tuple(data)


def render_help_menu(width, height):
    data = []

    data.append(to_braille('Move through the book by pressing the'))
    data.append(to_braille('arrow buttons on the front of the'))
    data.append(to_braille('machine. Hold them down to move 5 pages'))
    data.append(to_braille('at a time. The home menu shows you what'))
    data.append(to_braille('you can do with the side buttons from'))
    data.append(to_braille('the home menu or the book. View this by'))
    data.append(to_braille('pressing the middle button on the front.'))
    data.append(to_braille('Pressing the menu button again will'))
    data.append(to_braille('always return you to the book.'))

    # pad page with empty rows
    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)


def render(width, height, state):
    help_menu = state['help_menu']['visible']
    if help_menu:
        return render_help_menu(width, height)
    home_menu = state['home_menu_visible']
    book_n = state['book']
    book = state['books'][book_n]
    if home_menu:
        return render_home_menu(width, height, book)
    else:
        page = book.page
        data = book
        n = page * height
        return data[n: n + height]
