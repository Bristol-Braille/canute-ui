import os
import re
import xml.dom.minidom as minidom

from . import utility
from . import braille

FORM_FEED = re.compile('\f')


class BookFile(list):
    page = 0
    bookmarks = tuple()

    def __init__(self, filename, width, height):
        list.__init__(self)
        self.filename = filename
        ext = os.path.splitext(filename)[-1].lower()
        if ext == '.brf':
            pages = []
            page = []
            with open(filename) as f:
                for line in f:
                    line = line.replace('\n', '')
                    page.append(line)
                    if FORM_FEED.match(line):
                        page[-1] = page[-1].replace('\f', '')
                        # pad up to the next page
                        while len(page) < (height - 1):
                            page.append(' ' * width)
                    if len(page) == (height - 1):
                        pages.append(tuple(page))
                        page = []
            # pad the last page
            if len(page) > 0:
                while len(page) < (height - 1):
                    page.append(' ' * width)
                pages.append(tuple(page))
            lines = utility.flatten(pages)
            self.lines = tuple(convert(l) for l in lines)

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
                        line = (0,) * width
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
        return self.lines.__getitem__(i)


def convert(line):
    converted = []
    for char in line:
        converted.append(braille.alpha_to_pin_num(char))
    return converted
