
import logging
from .actions import get_max_pages, dimensions
from . import utility


log = logging.getLogger(__name__)


def render(state):
    width, height = dimensions(state['app'])
    location = state['app']['location']
    if location == 'library':
        page = state['app']['library']['page']
        data = state['app']['library']['data']
        # subtract title from page height
        data_height = height - 1
        max_pages = get_max_pages(data, data_height)
        n = page * data_height
        data = data[n: n + data_height]
        # pad page with empty rows
        while len(data) < data_height:
            data += ((0,) * width,)
        title = format_title('library menu', width, page, max_pages)
        set_display(tuple([title]) + tuple(data))
    elif location == 'menu':
        page = state['app']['menu']['page']
        data = state['app']['menu']['data']
        # subtract title from page height
        data_height = height - 1
        max_pages = get_max_pages(data, data_height)
        title = format_title('system menu', width, page, max_pages)
        n = page * data_height
        data = data[n: n + data_height]
        # pad page with empty rows
        while len(data) < data_height:
            data += ((0,) * width,)
        set_display(tuple([title]) + tuple(data))
    elif type(location) == int:
        page = state['app']['books'][location]['page']
        data = state['app']['books'][location]['data']
        n = page * height
        data = data[n: n + height]
        set_display(data)


row = 0
previous_data = []
display_data = []


def render_line(driver):
    global row
    global previous_data
    global display_data
    if row >= len(display_data):
        return
    while row >= len(previous_data):
        previous_data.append([])
    line = display_data[row]
    if line != previous_data[row]:
        driver.set_braille_row(row, line)
        previous_data[row] = line
    row += 1


def set_display(data):
    global display_data
    global row
    display_data = data
    row = 0


def format_title(title, width, page_number, total_pages):
    '''
    format a title like this:
        * title on the top line.
        * use two dot-six characters to indicate all uppercase for the title.
        * page numbers all the way at the right with 3 digits out of total,
        e.g. 001 / 003.
    '''
    # hack - leave space at the beginning for the uppercase symbols
    uppercase = '  '
    title = "%s%s" % (uppercase, title)
    current_page = " %03d / %03d" % (page_number + 1, total_pages + 1)

    available_title_space = width - len(current_page)

    # make title right length
    if len(title) > available_title_space:
        # truncate
        title = title[0:available_title_space]
    else:
        # pad
        title += " " * (available_title_space - len(title))

    title_pins = utility.alphas_to_pin_nums(title + current_page)
    # replace first 2 chars with the uppercase symbols
    title_pins[0:2] = [32, 32]
    return title_pins
