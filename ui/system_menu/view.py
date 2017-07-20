from .. import utility


def render(width, height, state):
    page = state['page']
    data = state['data']
    # subtract title from page height
    data_height = height - 1
    max_pages = utility.get_max_pages(data, data_height)
    title = utility.format_title('system menu', width, page + 1, max_pages + 1)
    n = page * data_height
    data = data[n: n + data_height]
    # pad page with empty rows
    while len(data) < data_height:
        data += ((0,) * width,)
    return tuple([title]) + tuple(data)
