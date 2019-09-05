# Manages indexing of books and returning pages on demand.
# Currently this is outsourced to an extension for speed.
import sys
import os
import ctypes
from ctypes import c_uint8, c_uint16, c_uint32, c_int32, c_char_p, Structure

LIBNAME = 'bookindex'

# Build an FFI for the extension.
prefix = {'win32': ''}.get(sys.platform, 'lib')
extension = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
lib = ctypes.cdll.LoadLibrary(prefix + LIBNAME + extension)


class PageExtentResult(Structure):
    _fields_ = [('status', c_int32),
                ('first', c_uint32),
                ('length', c_uint16)]

    def __str__(self):
        return '(status:{},first:{},length:{})'.format(self.status, self.first, self.length)


lib.init.argtypes = (c_uint8,)
lib.init.restype = c_int32

lib.trigger_load.argtypes = (c_char_p, c_int32)
lib.trigger_load.restype = None

lib.get_page_count.argtypes = (c_char_p,)
lib.get_page_count.restype = c_int32

lib.get_page.argtypes = (c_char_p, c_uint16)
lib.get_page.restype = PageExtentResult

# Syntactic sugar to hide the FFI-ness.
# Calls to os.path.exists(bookpath) are a cheap way to outsource
# embedded NUL detection (it'll throw ValueError).
init = lib.init

# FIXME get this from serial greeting or constant
init(9)


def trigger_load(bookpath, bookfd):
    os.path.exists(bookpath)
    lib.trigger_load(bookpath.encode(), bookfd)


def get_page_count(bookpath):
    os.path.exists(bookpath)
    return lib.get_page_count(bookpath.encode())


def get_page(bookpath, page):
    os.path.exists(bookpath)
    return lib.get_page(bookpath.encode(), page)
