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
    data.append(to_braille('view library menu'))
    data.append(to_braille('view system menu'))
    return tuple(data)


def render(width, height, state):
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
