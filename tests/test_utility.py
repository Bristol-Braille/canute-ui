import unittest
import os

import ui.utility as utility

dir_path = os.path.dirname(os.path.realpath(__file__))
test_books_dir = os.path.join(dir_path, 'test-books')


class TestUtility(unittest.TestCase):
    def test_find_files(self):
        self.assertEqual(len(utility.find_files(test_books_dir, ('brf',))), 2)
        self.assertEqual(len(utility.find_files(test_books_dir, ('pef',))), 1)
        self.assertEqual(
            len(utility.find_files(test_books_dir, ('brf', 'pef'))),
            3
        )
