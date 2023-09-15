import unittest
import os

from ui.library.explorer import Library

dir_path = os.path.dirname(os.path.realpath(__file__))
test_books_dir = [('test-books', 'test dir')]


class TestUtility(unittest.TestCase):
    def test_find_files(self):
        library = Library(dir_path, test_books_dir, ('brf',))
        self.assertEqual(len(library.book_files()), 2)
        library = Library(dir_path, test_books_dir, ('pef',))
        self.assertEqual(len(library.book_files()), 1)
        library = Library(dir_path, test_books_dir, ('brf', 'pef'))
        self.assertEqual(len(library.book_files()), 3)
