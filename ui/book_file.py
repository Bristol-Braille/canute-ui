import os

from . import braille


class BookFile(list):
    page = 0
    bookmarks = tuple()

    def __init__(self, filename, cells):
        list.__init__(self)
        self.filename = filename
        ext = os.path.splitext(filename)[-1].lower()
        if ext == '.brf':
            with open(filename) as f:
                self.lines = tuple(line for line in f)
        else:
            raise Exception(ext)

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, i):
        if type(i) is slice:
            return tuple(convert(l) for l in self.lines.__getitem__(i))
        else:
            return convert(self.lines[i])


def convert(line):
    converted = []
    for char in line:
        try:
            converted.append(braille.alpha_to_pin_num(char))
        except:
            pass
    return converted
