"""
Utility
=======

contains various utility methods used by many of the modules
"""

import os
import logging
log = logging.getLogger(__name__)


def get_pid_file():
    return os.path.dirname(os.path.realpath(__file__)) + "/ui.pid"

def write_pid_file():
    pid = str(os.getpid())
    file(get_pid_file(), 'w').write(pid)

def remove_pid_file():
    try:
        os.unlink(get_pid_file())
    except OSError:
        pass

def find_firmware(directory):
    '''recursively look for firmware, return first one found'''
    firmware_file = 'canute-firmware.zip'
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
                if filename == firmware_file:
                    return(os.path.join(root, filename))

def find_books(directory):
    '''return pef and canute format books'''
    return find_files(directory, ('.pef', '.canute'))

def find_files(directory, extensions):
    '''recursively look for files that end in the extensions tuple'''
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
                if filename.endswith(extensions):
                    matches.append(os.path.join(root, filename))
    return matches


def unicode_to_pin_num(uni_char):
    '''
    converts a unicode braille character to a decimal number that can then be used to load a picture to display the character
    used to convert PEF format to CANUTE format
    http://en.wikipedia.org/wiki/Braille_Patterns
    '''
    int_code = ord(uni_char) - 10240
    pin_num = 0
    pins = [0]*6
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
    return unichr(pin_num+10240)

''' for sorting & debugging '''
def pin_num_to_alpha(numeric):
    mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    return mapping[numeric]

def pin_nums_to_alphas(numerics):
    return map(pin_num_to_alpha, numerics)

''' used to convert plain text to pin pattern numbers '''
def alpha_to_pin_num(alpha):
    '''
    convert a single alpha, digit or some punctuation to 6 pin braille
    '''
    # mapping from http://en.wikipedia.org/wiki/Braille_ASCII#Braille_ASCII_values
    mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    alpha = alpha.upper()
    try:
        return mapping.index(alpha)
    except ValueError:
        log.warning("problem converting [%s] to braille pic" % alpha)
        return 0

def alphas_to_pin_nums(alphas):
    '''convert a list of alphas to pin numbers using :meth:`alpha_to_pin_num`'''
    return map(alpha_to_pin_num, alphas)

def test_book(dimensions):
    '''
    returns a book of 8 pages with each page showing all possible combinations of the 8 rotor positions
    '''
    text = []
    for i in range(8):
        char = i + (i << 3)
        for j in range(dimensions[1]):
            text.append([char] * dimensions[0])
    return text

def test_pattern(dimensions):
    '''creates a repeating pattern of all possible dot patterns'''
    cols, rows = dimensions
    text = []
    for i in range(cols * rows):
        text.append(i % 64)
    return text
