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
#   ^^^ adjust to trim away whitespace before '...' ?


# test code

def truncate_location(string, width):
    if len(string) < width:
        return string + '/'
    dirs = string.split(os.sep)
    last = dirs[-1]
    depth = len(dirs) - 1
    if len(last) + depth + 5 < width:
        spare = width - (len(last) + depth + 1)
        first = dirs[0]
        if len(first) < spare:
            extra = spare - len(first)
            if depth > 1 and extra > 5:
                parent = dirs[-2]
                return first + (depth - 1) * '/' + truncate_middle(parent, extra) + '/' + last + '/'
        if spare > 5:
            return truncate_middle(first, spare) + depth * '/' + last + '/'
    # no room for anything other than depth and dir name
    return depth * '/' + truncate_middle(last, width - depth - 1) +'/'


def atoi(text):
    return int(text) if text.isdigit() else text.lower()

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

class Directory:
    def __init__(self, name, parent = None):
        self.parent = parent
        self.name = name
        self.files = []

    @property
    def relpath(self):
        if self.parent is None:
            return self.name
        return os.path.join(self.parent.relpath, self.name)

    @property
    def files_count(self):
        return len(self.files)

    @property
    def files_pages(self):
        return math.ceil(self.files_count / Library.PAGE_SIZE)

    @property
    def _depth(self):
        depth = 1
        if self.parent is not None:
            depth += self.parent._depth
        return depth

    def display_text(self, show_count=True):
        extra = 0
        if show_count:
            count = self.files_count
            if count > 0:
                count_str = str(count)
                # 4 = ' - #' suffix
                extra = 4 + len(count_str)
        depth = self._depth
        # 39 takes into account the trailing slash
        title = truncate_middle(self.name.replace('_', ' '), 39 - depth - extra)
        display = depth * '-' + f"{to_display_text(from_ascii(title))}/"
        if extra > 0:
            # 41 takes into account the hyphen in extra
            pad = 41 - len(display) - extra
            display += ' ' + pad * '-' + ' #' + count_str
        return display


class File:
    def __init__(self, name, directory):
        self.directory = directory
        self.name = name

    @property
    def title(self):
        title = os.path.splitext(self.name)[0].replace('_', ' ')
        return truncate_middle(title, 40)
    
    def display_text(self):
        return to_display_text(from_ascii(self.title))

class Library:
    '''
    Makes the assumption that the filesystem _won't_ change
    while being viewed (this is reasonable on a Canute)
    '''
    PAGE_SIZE = 8

    def __init__(self, start_dir):
        self.start_dir = os.path.abspath(os.path.split(start_dir)[0])
        root = Directory(os.path.basename(start_dir))
        self.walk(root)
        self.prune(root)
        self.dirs = []
        self.flatten(root)
        self.dir_count = len(self.dirs)
        self.files_dir_index = None
        self.files_count = 0

    def walk(self, root):
        '''
        Walk the file system looking for brfs and pefs
        '''
        dirs = []
        files = []
        for entry in os.scandir(os.path.join(self.start_dir, root.relpath)):
            if entry.is_dir(follow_symlinks=False) and \
                    entry.name[0] != '.' and entry.name[0] != '$':
                dirs.append(entry.name)
            elif entry.is_file():
                ext = os.path.splitext(entry.name)[1].lower()
                if ext == '.brf' or ext == '.pef':
                    files.append(entry.name)

        dirs.sort(key=natural_keys)
        root.dirs = [Directory(dir, root) for dir in dirs]
        for dir in root.dirs:
            self.walk(dir)

        files.sort(key=natural_keys)
        root.files = [File(f, root) for f in files]

    def prune(self, root):
        '''
        Remove any folders with 0 files in (depth first)
        '''
        root.dirs[:] = [dir for dir in root.dirs if not self.prune(dir)]
        return len(root.dirs) == 0 and root.files_count == 0

    def flatten(self, root):
        '''
        Populate the self.dirs list (breadth first)
        '''
        self.dirs.append(root)
        for dir in root.dirs:
            self.flatten(dir)
        # tidy up, as we no longer need a two-way tree
        del root.dirs

    @property
    def pages(self):
        pages = self._dirs_pages
        if self.files_count > 0:
            # + 1 for the extra dir page before/after
            pages += self._files_pages + 1
        return pages

    def _page_display_text(self, dir, page, of_pages):
        title = ',,LIBR>Y M5U'
        progress = f"#{page}/#{of_pages}"
        if dir is not None:
            title += ' - ' + truncate_location(dir.relpath, 25 - len(progress) - 3)
        title += ' ' + (40 - len(title) - len(progress) - 2) * '-' + ' ' + progress
        return to_display_text(from_ascii(title))

    @property
    def _files_page_open(self):
        return self.files_dir_index is not None

    @property
    def _files_page_start(self):
        '''only valid if files_dir_index is open'''
        return math.ceil(self.files_dir_index / Library.PAGE_SIZE)

    @property
    def _files_pages(self):
        return math.ceil(self.files_count / Library.PAGE_SIZE)

    @property
    def _dirs_pages(self):
        return math.ceil(self.dir_count / Library.PAGE_SIZE)

    def _is_files_page(self, page_num):
        if self._files_page_open:
            files_pages = self._files_pages
            files_start = self._files_page_start
            return page_num >= files_start and page_num < files_start + files_pages
        return False

    def canonical_dir_page(self, page_num):
        if self._files_page_open and page_num >= self._files_page_start:
            # remove one extra to 'split' the current menu page and show it
            # before and after the current file list
            page_num -= min(self._files_pages, page_num - self._files_page_start) + 1
        return page_num

    def get_page(self, page_num):
        if self._is_files_page(page_num):
            page_num -= self._files_page_start
            offset = page_num * Library.PAGE_SIZE
            dir = self.dirs[self.files_dir_index]
            yield self._page_display_text(dir, page_num + 1, dir.files_pages), None
            for file in dir.files[offset:offset+Library.PAGE_SIZE]:
                yield file.display_text(), None
            return

        page_num = self.canonical_dir_page(page_num)
        start = page_num * Library.PAGE_SIZE
        for i in range(start, min(start + Library.PAGE_SIZE, len(self.dirs))):
            dir = self.dirs[i]
            if i == start:
                yield self._page_display_text(dir.parent, page_num + 1, self._dirs_pages), None                
            yield dir.display_text(self.files_dir_index != i), i if dir.files_count > 0 else None

    def set_files_dir_index(self, index):
        old_count = self.files_count
        self.files_dir_index = index
        if index is None:
            self.files_count = 0
        else:
            self.files_count = self.dirs[index].files_count
        return self._files_page_start if self._files_page_open else None


def main(stdscr):
    page = 0
    library = Library(sys.argv[1])
    key = ''

    while not (key == 'x' or key == 'q'):
        stdscr.clear()
        i = 0
        dirs = []
        # stdscr.addstr(0, 0, key)
        for display, dir_index in library.get_page(page):
            stdscr.addstr(i, 0, display)
            dirs.append(dir_index)
            i += 1

        stdscr.refresh()
        key = stdscr.getkey()
        if (key == 'KEY_LEFT' or key == 'KEY_UP'):
            page -= 1
            if page < 0:
                page = 0
        elif key == 'KEY_RIGHT' or key == 'KEY_DOWN':
            page += 1
            if page >= library.pages:
                page = library.pages - 1
        elif key.isdigit():
            option = atoi(key) - 1
            dir_page = library.canonical_dir_page(page)
            # align display to top of file list
            new_page = library.set_files_dir_index(dirs[option])
            if new_page is not None:
                page = new_page
            else:
                page = dir_page

if __name__ == '__main__':
    curses.wrapper(main)
