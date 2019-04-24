import logging
from curses.ascii import isspace, isprint
log = logging.getLogger(__name__)

UNICODE_BRAILLE_BASE = 0x2800


def format_title(title, width, page_number, total_pages, capitalize=True):
    '''
    format a title like this:
        * title on the top line.
        * use two dot-six characters to indicate all uppercase for the title.
        * page numbers all the way at the right,
        e.g. ',,library menu               #1/#3'.
    '''
    # ',, indicates all uppercase'
    if capitalize:
        title = ',,' + title

    page_number += 1

    current_page = ' {}/{}'.format(to_ueb_number(page_number),
                                   to_ueb_number(total_pages))

    available_title_space = width - len(current_page)

    # make title right length
    title_length = len(title)
    if title_length > available_title_space:
        # truncate
        title = truncate_middle(title, available_title_space)
    else:
        # pad
        title += ' '
        if (title_length - 1) <= available_title_space:
            title += '-' * (available_title_space - title_length - 1)

    return from_ascii(title + current_page)


def truncate_middle(string, width):
    if len(string) <= width:
        return string

    words = string.split(' ')
    last = words[-1]

    width_available = width - len(last) - 4

    if width_available < 3:
        return string[0:width - 3] + '...'

    return string[0:width_available] + '... ' + last


ueb_number_mapping = 'JABCDEFGHI'


def to_ueb_number(n):
    ueb_number = '#'
    for c in str(n):
        ueb_number += ueb_number_mapping[int(c)]
    return ueb_number


def unicode_to_pin_num(uni_char):
    '''
    converts a unicode braille character to a decimal number

    used to convert PEF format to CANUTE format
    http://en.wikipedia.org/wiki/Braille_Patterns
    '''
    int_code = ord(uni_char) - UNICODE_BRAILLE_BASE
    pin_num = 0
    pins = [0] * 6
    if int_code >= 0x20:
        int_code -= 0x20
        pins[5] = 1
        pin_num += 32
    if int_code >= 0x10:
        int_code -= 0x10
        pins[4] = 1
        pin_num += 16
    if int_code >= 0x8:
        int_code -= 0x8
        pins[3] = 1
        pin_num += 8
    if int_code >= 0x4:
        int_code -= 0x4
        pins[2] = 1
        pin_num += 4
    if int_code >= 0x2:
        int_code -= 0x2
        pins[1] = 1
        pin_num += 2
    if int_code >= 0x1:
        int_code -= 0x1
        pins[0] = 1
        pin_num += 1

    return pin_num


def pin_num_to_unicode(pin_num):
    '''
    used by the gui to display braille
    '''
    return chr(pin_num + UNICODE_BRAILLE_BASE)


# mapping from
# http://en.wikipedia.org/wiki/Braille_ASCII#Braille_ASCII_values
mapping = ' A1B\'K2L@CIF/MSP"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)='


def pin_num_to_alpha(numeric):
    ''' for sorting & debugging '''
    return mapping[numeric]


def pin_nums_to_alphas(numerics):
    ''' used to convert plain text to pin pattern numbers '''
    return list(map(pin_num_to_alpha, numerics))


def alpha_to_pin_num(alpha):
    '''
    convert a single alpha, digit or some punctuation to 6 pin braille
    unknown characters will be logged and a space will be returned.
    '''
    alpha = alpha.upper()
    try:
        return mapping.index(alpha)
    except ValueError:
        return 0


def from_ascii(alphas):
    '''
    convert a list or string of alphas to pin numbers using
    :meth:`alpha_to_pin_num` form feed and line feed characters are supressed
    '''
    return tuple(alpha_to_pin_num(a) for a in alphas)


def from_unicode(alphas):
    '''
    convert a list or string of unicode chars to pin numbers using
    :meth:`unicode_to_pin_num` form feed and line feed characters are supressed
    '''
    return tuple(unicode_to_pin_num(a) for a in alphas)


def alpha_to_unicode(alpha):
    '''
    Convert an alpha to a Unicode character.
    '''
    alpha = alpha.upper()
    try:
        if isprint(alpha):  # includes ASCII space, 0x20
            return chr(UNICODE_BRAILLE_BASE + mapping.index(alpha))
        elif isspace(alpha):
            return alpha
        else:
            return chr(UNICODE_BRAILLE_BASE)
    except ValueError:
        return 0


def alphas_to_unicodes(alphas):
    '''
    Convert an alpha string to a Unicode string.
    '''
    return ''.join(map(alpha_to_unicode, alphas))
