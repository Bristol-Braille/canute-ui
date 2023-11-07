import os
import math
import logging

from ..book import book_file
from .. import state


log = logging.getLogger(__name__)


class LibraryState:
    def __init__(self, root: 'state.RootState'):
        self.root = root

        self.page = 0
        self.media_dir = ''
        self.dirs = []
        # index of directory that is currently expanded, if any
        self.files_dir_index = None
        self.files_count = 0

    @property
    def DIRS_PAGE_SIZE(self):
        width, height = self.root.app.dimensions
        return height - 1

    @property
    def FILES_PAGE_SIZE(self):
        width, height = self.root.app.dimensions
        return height - 2

    @property
    def dir_count(self):
        return len(self.dirs)

    @property
    def open_dir(self):
        return self.dirs[self.files_dir_index] if self.files_page_open else None

    @property
    def files_page_open(self):
        return self.files_dir_index is not None

    @property
    def _files_page_start(self):
        """only valid if files_dir_index is open"""
        return math.ceil((self.files_dir_index + 1) / self.DIRS_PAGE_SIZE)

    @property
    def _files_pages(self):
        return math.ceil(self.files_count / self.FILES_PAGE_SIZE)

    @property
    def _dirs_pages(self):
        return math.ceil(self.dir_count / self.DIRS_PAGE_SIZE)

    @property
    def pages(self):
        pages = self._dirs_pages
        if self.files_page_open:
            # + 1 for the extra dir page before/after
            pages += self._files_pages + 1
        return pages

    def _is_files_page(self, page_num):
        if self.files_page_open:
            files_pages = self._files_pages
            files_start = self._files_page_start
            return page_num >= files_start and page_num < files_start + files_pages
        return False

    def canonical_dir_page(self, page_num):
        if self.files_page_open and page_num >= self._files_page_start:
            # remove one extra to 'split' the current menu page and show it
            # before and after the current file list
            page_num -= min(self._files_pages, page_num - self._files_page_start) + 1
        return page_num

    def book_from_file(self, file):
        return self.root.app.user.books[file.relpath]

    def page_begin_end(self, page_num):
        begin = 0
        end = self.DIRS_PAGE_SIZE
        if self.files_page_open:
            if page_num == self._files_page_start - 1:
                end = self.files_dir_index % self.DIRS_PAGE_SIZE + 1
            if page_num == self._files_page_start + self._files_pages:
                begin = self.files_dir_index % self.DIRS_PAGE_SIZE
        return begin, end

    def action(self, button):
        """this mirrors the view render code"""
        page_num = self.page

        begin, end = self.page_begin_end(page_num)

        if self._is_files_page(page_num):
            page_num -= self._files_page_start
            offset = page_num * self.FILES_PAGE_SIZE
            dir = self.open_dir
            if button == 0:
                return  # title
            elif button == 1:
                self.set_files_dir_index(None)  # back
            else:
                i = button - 2
                if i >= begin and i < end and offset + i < len(dir.files):
                    file = dir.files[offset + i]
                    self.open_book(self.book_from_file(file))
                    return
                else:
                    return  # blank
            return

        page_num = self.canonical_dir_page(page_num)
        start = page_num * self.DIRS_PAGE_SIZE
        if button == 0:
            return  # title
        else:
            i = button - 1
            index = start + i
            if i >= begin and i < end and index < self.dir_count:
                dir = self.dirs[index]
                if dir.files_count > 0:
                    self.set_files_dir_index(index)  # directory to open
                # else empty dir
                return
            elif (i == 0 or i == self.DIRS_PAGE_SIZE - 1) and index < self.dir_count:
                self.set_files_dir_index(None)  # more
            else:
                return  # blank

    def set_files_dir_index(self, index):
        dir_page = self.canonical_dir_page(self.page)
        self.files_dir_index = index
        if index is None:
            self.files_count = 0
        else:
            self.files_count = self.dirs[index].files_count
        if self.files_page_open:
            self.page = self._files_page_start
        else:
            self.page = dir_page
        self.root.refresh_display()

    def show_files_dir(self, book):
        """open the folder that this book is in"""
        relpath = os.path.dirname(book)
        name = os.path.basename(book)
        for index, dir in enumerate(self.dirs):
            if dir.relpath == relpath:
                self.files_dir_index = index
                self.files_count = dir.files_count
                for index, file in enumerate(dir.files):
                    if file.name == name:
                        file_page = math.floor(index / self.FILES_PAGE_SIZE)
                        self.page = self._files_page_start + file_page
                        break
                break

    def open_book(self, book):
        self.root.app.user.current_book = book.relpath(self.media_dir)
        self.root.app.location = 'book'
        self.root.app.home_menu_visible = False
        self.root.refresh_display()
        self.root.save_state()

    def add_or_replace(self, book):
        relpath = os.path.relpath(book.filename, start=self.media_dir)
        self.root.app.user.books[relpath] = book

    def set_book_loading(self, book):
        book = book._replace(load_state=book_file.LoadState.LOADING)
        self.add_or_replace(book)

    def _books_on(self, page_num):
        begin, end = self.page_begin_end(page_num)

        if self._is_files_page(page_num):
            page_num -= self._files_page_start
            offset = page_num * self.FILES_PAGE_SIZE
            dir = self.open_dir
            for i in range(0, self.FILES_PAGE_SIZE):
                if i >= begin and i < end and offset + i < len(dir.files):
                    file = dir.files[offset + i]
                    book = self.book_from_file(file)
                    yield book

    def books_to_index(self):
        now = [self.root.app.user.book]

        if self.root.app.location == 'library':
            now += list(self._books_on(self.page))

            # cache any books needed for reachable directory pages
            later = []
            page_num = self.page
            if not self._is_files_page(page_num):
                page_num = self.canonical_dir_page(page_num)
                start = page_num * self.DIRS_PAGE_SIZE
                begin, end = self.page_begin_end(page_num)
                for i in range(0, self.DIRS_PAGE_SIZE):
                    index = start + i
                    if i >= begin and i < end and index < self.dir_count:
                        dir = self.dirs[index]
                        for i in range(0, min(dir.files_count, self.FILES_PAGE_SIZE)):
                            file = dir.files[i]
                            book = self.book_from_file(file)
                            later.append(book)

            # and any reachable by next/prev
            for page in [page_num-5, page_num-1, page_num+1, page_num+5]:
                if page > 0 and page < self.pages:
                    later += list(self._books_on(page))
        else:
            # not looking at a library page, so only need to cache current page
            later = list(self._books_on(self.page))

        now = [b for b in now if b.load_state == book_file.LoadState.INITIAL]
        later = [b for b in later if b.load_state == book_file.LoadState.INITIAL]

        return now, later
