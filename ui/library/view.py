from .. import utility

to_braille = utility.to_braille


def render_help_menu(width, height, page):
    data = []
    if page == 0:
        data.append(to_braille('Choose the book you wish to read by'))
        data.append(to_braille('pressing the button to the left of the'))
        data.append(to_braille('title.  Press the right arrow button to'))
        data.append(to_braille('find more books in the library, if there'))
        data.append(to_braille('are more than 8.  If you cannot find the'))
        data.append(to_braille('book you are looking for, you may wish'))
        data.append(to_braille('to change the order in which the titles'))
        data.append(to_braille('appear, by going back to the system menu'))
        data.append(to_braille('and Choosing a different order.'))
    elif page == 1:
        data.append(to_braille('The system menu can be reached by'))
        data.append(to_braille('pressing the button with the letter M'))
        data.append(to_braille('twice on it, then choosing button 9'))
        data.append(to_braille('where the line says "System Menu". The'))
        data.append(to_braille('choices are "Most recently read, at the'))
        data.append(to_braille('top" or "In alphabetical order"'))

    while len(data) < height:
        data.append((0,) * width)

    return tuple(data)


def render_library(width, height, state):
    page = state['library']['page']
    books = state['books']
    # subtract title from page height
    data_height = height - 1
    max_pages = utility.get_max_pages(books, data_height)
    title = utility.format_title('library menu', width, page, max_pages)
    data = [title]
    n = page * data_height
    for book in books[n:n + data_height]:
        max_pages = utility.get_max_pages(book, height)
        data.append(utility.format_title(book.title, width, book.page,
                                         max_pages, capitalize=False))

    # pad page with empty rows
    while len(data) < height:
        data.append((0,) * width)

    print(data)

    return tuple(data)


def render(width, height, state):
    if state['help_menu']['visible']:
        return render_help_menu(width, height, state['help_menu']['page'])
    else:
        return render_library(width, height, state)
