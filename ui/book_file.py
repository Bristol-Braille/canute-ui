import os
import xml.dom.minidom as minidom

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
        elif ext == '.pef':
            xml_doc = minidom.parse(filename)
            pages = xml_doc.getElementsByTagName('page')
            lines = []
            for page in pages:
                for row in page.getElementsByTagName('row'):
                    try:
                        data = row.childNodes[0].data.rstrip()
                        line = []
                        for uni_char in data:
                            pin_num = braille.unicode_to_pin_num(uni_char)
                            line.append(pin_num)
                    except IndexError:
                        # empty row element
                        line = [0] * cells
                    lines.append(line)
            self.lines = tuple(lines)
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
