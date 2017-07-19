

def render (width, height, state):
    book = state['book']
    page = state['books'][book]['page']
    data = state['books'][book]['data']
    n = page * height
    return data[n: n + height]
