#!/usr/bin/env python3
import sys
import os
import re
import math
import curses

# lifted from existing code
mapping = ' A1B\'K2L@CIF/MSP"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)='
def alpha_to_pin_num(alpha):
    if ord(alpha) >= 0x60:
        alpha = chr(ord(alpha) - 0x20)

    try:
        return mapping.index(alpha)
    except ValueError:
        return 0
def from_ascii(alphas):
    return tuple(alpha_to_pin_num(a) for a in alphas)
def pin_num_to_alpha(numeric):
    return mapping[numeric]
def to_display_text(pin_nums):
    return ''.join(map(pin_num_to_alpha, pin_nums))
def truncate_middle(string, width):
    if len(string) <= width:
        return string
    words = string.split(' ')
    last = words[-1]
    width_available = width - len(last) - 4
    if width_available < 3:
        return string[0:width - 3] + '...'
    return string[0:width_available] + '... ' + last

# test code

def atoi(text):
    return int(text) if text.isdigit() else text.lower()

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


class Library:
    '''
    Makes the assumption that the filesystem _won't_ change
    while being viewed (this is reasonable on a Canute)
    '''
    def __init__(self, start_dir):
        self.start_dir = os.path.abspath(start_dir)
        self.dir_count = self.count_dirs()
        self.files_dir = None
        self.files_count = 0

    def walk(self):
        for root, dirs, files in os.walk(self.start_dir):
            # remove 'hidden' dot dirs
            dirs[:] = [d for d in dirs if not d[0] == '.']
            # sort into human alpha num order
            dirs.sort(key=natural_keys)
            yield root, dirs, files

    def count_dirs(self):
        count = 0
        for root, dirs, files in self.walk():
            count += 1
        return count

    @property
    def pages(self):
        return math.ceil(self.rows / 8)

    @property
    def rows(self):
        return self.dir_count + self.files_count

    def _page_title(self, dir):
        path = os.path.relpath(dir, os.path.split(self.start_dir)[0])
        title = ',,LIBR>Y M5U'
        if not path == '.':
            title += ' - ' + path + '/'
        return title


    def get_page(self, start):
        count = 0
        for root, dirs, files in self.walk():
            count += 1

            if count > start:
                if count == start + 1:
                    title = self._page_title(os.path.split(root)[0])
                    yield to_display_text(from_ascii(title)), None

                rel_path = os.path.relpath(root, self.start_dir)
                segments = rel_path.split(os.sep)
                depth = 1 if rel_path == '.' else len(segments) + 1
                title = truncate_middle(os.path.basename(root).replace('_', ' '), 40 - depth - 2)
                display = depth * '-' + f"{to_display_text(from_ascii(title))}/"
                yield display, root
                if count == start + 8:
                    return

            if root == self.files_dir:
                files = [f for f in files if not f[0] == '.']
                files.sort(key=natural_keys)
                for file in files:
                    count += 1
                    if count > start:
                        if count == start + 1:
                            title = self._page_title(root)
                            yield to_display_text(from_ascii(title)), None
                        title = truncate_middle(os.path.splitext(file)[0].replace('_', ' '), 40)
                        yield to_display_text(from_ascii(title)), None
                        if count == start + 8:
                            return

    def set_files_dir(self, files_dir):
        self.files_dir = files_dir
        if files_dir is None:
            self.files_count = 0
        else:
            self.files_count = len(os.listdir(files_dir))


def main(stdscr):
    row = 0
    library = Library(sys.argv[1])
    key = ''

    while not (key == 'x' or key == 'q'):
        stdscr.clear()
        i = 0
        dirs = []
        # stdscr.addstr(0, 0, key)
        for display, dir in library.get_page(row):
            stdscr.addstr(i, 0, display)
            dirs.append(dir)
            i += 1

        stdscr.refresh()
        key = stdscr.getkey()
        if (key == 'KEY_LEFT' or key == 'KEY_UP'):
            row -= 8
            if row < 0:
                row = 0
        elif key == 'KEY_RIGHT' or key == 'KEY_DOWN':
            row += 8
        elif key.isdigit():
            option = atoi(key) - 1
            library.set_files_dir(dirs[option])
            # align display to top of file list
            row += option

if __name__ == '__main__':
    curses.wrapper(main)
