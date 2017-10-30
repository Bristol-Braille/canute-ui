import os

class Book(list):
    def __init__(self, filename, cells):
        list.__init__(self)
        self.filename = filename
        ext = os.path.splitext(filename)[-1].lower()
        if ext == '.brf':
            with open(filename) as f:
                self.lines = tuple(line for line in f)

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, i):
        return self.lines.__getitem__(i)
