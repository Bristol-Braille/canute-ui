import os

class Book(list):
    def __init__(self, filename, cells):
        list.__init__(self)
        self.filename = filename
        ext = os.path.splitext(filename)[-1].lower()
        if ext == '.brf':
            self.num_lines = sum(1 for line in open(filename))

    @property
    def title(self):
        basename = os.path.basename(self.filename)
        title = os.path.splitext(basename)[0].replace('_', ' ')
        return title

    def __len__(self):
        return self.num_lines
