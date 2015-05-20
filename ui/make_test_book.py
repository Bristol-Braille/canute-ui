from utility import test_book
from pageable import Library

dimensions = (28,4) #canute

pages = test_book(dimensions)
native_file = Library.book_dir + 'test' + Library.native_ext

with open(native_file, 'w') as fh:
    for page in pages:
        line = ','.join([str(x) for x in page])
        fh.write(line + "\n")

