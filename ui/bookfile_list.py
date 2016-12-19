import logging
import os
import struct
log = logging.getLogger(__name__)


class BookFile_List(list):
    '''represents a file as a Python list. Only supports len and slices

    :param filename: the file to open
    :param dimensions: display dimensions tuple
    '''
    def __init__(self, filename, cells):
        list.__init__(self)
        self.cells = cells
        self.filename = filename
        statinfo = os.stat(filename)
        self.num_pages = statinfo.st_size / self.cells

    def __len__(self):
        return self.num_pages

    def __getslice__(self, i, j):
        log.debug("requested lines %d to %d" % (i, j))
        with open(self.filename) as fh:
            pages = []
            for pos in range(i, j):
                fh.seek(pos * self.cells)
                data = fh.read(self.cells)
                try:
                    page = struct.unpack("%db" % self.cells, data)
                except struct.error:    
                    page = [0] * self.cells
                pages.append(page)

        return pages

if __name__ == '__main__':
    book = BookFile_List('./bookfile_list.py', 32)
    print(book[2:8])
