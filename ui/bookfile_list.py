import logging
import os
import struct
log = logging.getLogger(__name__)

class BookFile_List(list):
    def __init__(self, filename, dimensions):
        list.__init__(self)
        self.cells = dimensions[0]
        self.rows = dimensions[1]
        self.filename = filename
        statinfo = os.stat(filename)
        self.num_pages = statinfo.st_size / self.cells

    def __len__(self):
        return self.num_pages

    def __getslice__(self, i, j):
        log.debug("requested lines %d to %d" % (i, j))
        with open(self.filename) as fh:
            pages = []
            for pos in range(i,j):
                fh.seek(pos * self.cells)
                data = fh.read(self.cells)
                page = struct.unpack("%db" % self.cells, data)
                pages.append(page)

        return pages

if __name__ == '__main__':
    book = BookFile_List('./bookfile_list.py', [28,4])
    print book[2:8]

