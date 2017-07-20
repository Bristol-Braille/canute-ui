import logging
import os
import struct
log = logging.getLogger(__name__)


class BookFile_List(list):
    '''represents a file as a Python list. Only supports len and slices

    :param filename: the file to open
    :param dimensions: display dimensions tuple
    '''

    page = 0

    def __init__(self, filename, cells):
        list.__init__(self)
        self.cells = cells
        self.filename = filename
        statinfo = os.stat(filename)
        self.num_lines = statinfo.st_size // self.cells

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    def __len__(self):
        return self.num_lines

    def __getitem__(self, i):
        if type(i) is slice:
            log.debug('requested lines %d to %d' % (i.start, i.stop))
            with open(self.filename, 'rb') as fh:
                lines = []
                for pos in range(i.start, i.stop):
                    fh.seek(pos * self.cells)
                    data = fh.read(self.cells)
                    try:
                        line = struct.unpack('%db' % self.cells, data)
                    except struct.error:
                        line = [0] * self.cells
                    lines.append(line)

            return lines
