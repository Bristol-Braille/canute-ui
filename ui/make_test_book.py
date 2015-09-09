from utility import test_book
from pageable import Library
from ConfigParser import ConfigParser

dimensions = (28,4) #canute
config = ConfigParser()
config.read('config.rc')

pages = test_book(dimensions)
book_dir = config.get('files', 'library_dir')
native_file = book_dir + 'test' + Library.native_ext

with open(native_file, 'w') as fh:
    for page in pages:
        fh.write(bytearray(page))

