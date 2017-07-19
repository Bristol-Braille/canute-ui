from .. import utility

to_braille = utility.to_braille

def render_home_menu(width, height, state):
    return tuple([[0] * 40] * 9)



def render(width, height, state):
    home_menu = state['home_menu_visible']
    book_n = state['book']
    book = state['books'][book_n]
    if home_menu:
        return render_home_menu(width, height, book)
    else:
        page = book['page']
        data = book['data']
        n = page * height
        return data[n: n + height]
