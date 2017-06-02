"""
Utility
=======

contains various utility methods used by many of the modules
"""

import os
import re
import logging
from collections import OrderedDict
from frozendict import frozendict, FrozenOrderedDict
import collections
log = logging.getLogger(__name__)


class FormfeedConversionException(Exception):
    pass


class LinefeedConversionException(Exception):
    pass


def find_ui_update(config):
    '''
    recursively look for firmware in the usb_dir,
    firmware file is called canute-ui.tar.gz
    returns first one found
    '''
    usb_dir = config.get('files', 'usb_dir')
    ui_file = 'canute-ui.tar.gz'

    log.info("update UI - looking for new ui in %s" % usb_dir)
    for root, dirnames, filenames in os.walk(usb_dir):
        for filename in filenames:
            if filename == ui_file:
                return(os.path.join(root, filename))


def find_files(directory, extensions):
    '''recursively look for files that end in the extensions tuple (case
    insensitive)'''
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            for ext in extensions:
                if re.search('\.' + ext + '$', filename, re.I):
                    matches.append(os.path.join(root, filename))
                    break
    return matches


def unicode_to_pin_num(uni_char):
    '''
    converts a unicode braille character to a decimal number that can then be
    used to load a picture to display the character

    used to convert PEF format to CANUTE format
    http://en.wikipedia.org/wiki/Braille_Patterns
    '''
    int_code = ord(uni_char) - 10240
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


'''
used by the gui to display braille
'''


def pin_num_to_unicode(pin_num):
    return chr(pin_num + 10240)


''' for sorting & debugging '''


def pin_num_to_alpha(numeric):
    mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,"
    mapping += "*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    return mapping[numeric]


def pin_nums_to_alphas(numerics):
    return list(map(pin_num_to_alpha, numerics))


''' used to convert plain text to pin pattern numbers '''


def alpha_to_pin_num(alpha):
    '''
    convert a single alpha, digit or some punctuation to 6 pin braille
    will raise Formfeed or Linefeed ConversionExceptions if they are found
    other unknown characters will be logged and a space will be returned.
    '''
    # mapping from
    # http://en.wikipedia.org/wiki/Braille_ASCII#Braille_ASCII_values
    mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,"
    mapping += "*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    alpha = alpha.upper()
    try:
        return mapping.index(alpha)
    except ValueError:
        # form feed
        if ord(alpha) == 12:
            raise FormfeedConversionException()
        if ord(alpha) == 10:
            raise LinefeedConversionException()
        log.warning("problem converting char #[%s] to pin number" % ord(alpha))
        return 0


def alphas_to_pin_nums(alphas):
    '''
    convert a list of alphas to pin numbers using :meth:`alpha_to_pin_num`
    form feed and line feed characters are supressed
    '''
    pin_nums = []
    for alpha in alphas:
        try:
            pin_nums.append(alpha_to_pin_num(alpha))
        except FormfeedConversionException():
            pass
        except LinefeedConversionException():
            pass
    return pin_nums


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


def test_pattern(dimensions):
    '''creates a repeating pattern of all possible dot patterns'''
    cols, rows = dimensions
    text = []
    for i in range(cols * rows):
        text.append(i % 64)
    return text


def flatten(l):
    return [item for sublist in l for item in sublist]


def pad_line(w, line):
    line.extend([0] * (w - len(line)))
    return line


def get_methods(cls):
    methods = [
        x for x in dir(cls)
        if isinstance(getattr(cls, x), collections.Callable)
    ]
    return [x for x in methods if not x.startswith('__')]


def unfreeze(frozen):
    if type(frozen) is tuple or type(frozen) is list:
        return list(unfreeze(x) for x in frozen)
    elif type(frozen) is OrderedDict or type(frozen) is FrozenOrderedDict:
        return OrderedDict([(k, unfreeze(v)) for k, v in list(frozen.items())])
    elif type(frozen) is dict or type(frozen) is frozendict:
        return {k: unfreeze(v) for k, v in list(frozen.items())}
    else:
        return frozen


def freeze(writable):
    if type(writable) is tuple or type(writable) is list:
        return tuple(freeze(x) for x in writable)
    elif type(writable) is OrderedDict or type(writable) is FrozenOrderedDict:
        return FrozenOrderedDict([(k, freeze(v)) for k, v in writable.items()])
    elif type(writable) is dict or type(writable) is frozendict:
        return frozendict({k: freeze(v) for k, v in writable.items()})
    else:
        return writable
