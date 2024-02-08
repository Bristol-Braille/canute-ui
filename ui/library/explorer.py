import os
import re
import math


def atoi(text):
    return int(text) if text.isdigit() else text.lower()


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


class Directory:
    def __init__(self, name, parent=None, display=None):
        self.parent = parent
        self.name = name
        self.display = display
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
        return math.ceil(self.files_count / Library.FILES_PAGE_SIZE)

    @property
    def _depth(self):
        depth = 1
        if self.parent is not None:
            depth += self.parent._depth
        return depth

    @property
    def display_name(self):
        return self.name.replace('_', ' ') if self.display is None else self.display

    @property
    def display_relpath(self):
        if self.parent is None:
            return self.display_name
        return os.path.join(self.parent.display_relpath, self.display_name)


class File:
    def __init__(self, name, directory):
        self.directory = directory
        self.name = name

    @property
    def relpath(self):
        return os.path.join(self.directory.relpath, self.name)


class LocalFile:
    def __init__(self, name):
        self.name = name

    @property
    def relpath(self):
        return self.name


class Library:
    """
    Makes the assumption that the filesystem _won't_ change
    while being viewed (this is reasonable on a Canute)
    """
    DIRS_PAGE_SIZE = 8
    FILES_PAGE_SIZE = 7

    def __init__(self, source_dirs, file_exts):
        self.file_exts = file_exts
        self.dirs = []

        for source_dir in source_dirs:
            source_path = source_dir.get('path')
            if not source_dir.get('mountpoint', False) or os.path.ismount(source_path):
                root = Directory(source_path, display=source_dir.get('name'))
                self.walk(root)
                self.prune(root)
                if len(root.dirs) > 0 or root.files_count > 0:
                    self.flatten(root)

        self.dir_count = len(self.dirs)
        self.files_dir_index = None
        self.files_count = 0

    def walk(self, root):
        """
        Walk the file system looking for brfs and pefs, avoid hidden files and
        OS recycling directories
        """
        dirs = []
        files = []
        for entry in os.scandir(root.relpath):
            if entry.is_dir(follow_symlinks=False) and \
                    entry.name[0] != '.' and \
                    entry.name != 'RECYCLE' and \
                    entry.name != '$Recycle':
                dirs.append(entry.name)
            elif entry.is_file():
                ext = os.path.splitext(entry.name)[1].lower()
                if entry.name[0] != '.' and ext[1:] in self.file_exts:
                    files.append(entry.name)

        dirs.sort(key=natural_keys)
        root.dirs = [Directory(dir, root) for dir in dirs]
        for dir in root.dirs:
            self.walk(dir)

        files.sort(key=natural_keys)
        root.files = [File(f, root) for f in files]

    def prune(self, root):
        """
        Remove any folders with 0 files in (depth first)
        """
        root.dirs[:] = [dir for dir in root.dirs if not self.prune(dir)]
        return len(root.dirs) == 0 and root.files_count == 0

    def flatten(self, root):
        """
        Populate the self.dirs list (breadth first)
        """
        self.dirs.append(root)
        for dir in root.dirs:
            self.flatten(dir)
        # tidy up, as we no longer need a two-way tree
        del root.dirs

    def book_files(self):
        books = []
        for dir in self.dirs:
            for file in dir.files:
                books.append(file.relpath)
        return books
