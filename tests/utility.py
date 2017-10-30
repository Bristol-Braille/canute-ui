def test_book(dimensions, content=None):
    '''
    returns a book of 8 pages with each page showing all possible combinations
    of the 8 rotor positions
    '''
    text = []
    for i in range(8):
        char = i + (i << 3)
        for j in range(dimensions[1]):
            if content is not None:
                text.append([content] * dimensions[0])
            else:
                text.append([char] * dimensions[0])
    return text
