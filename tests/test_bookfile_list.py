import unittest
import os
from . import utility
from ui.bookfile_list import BookFile_List


class TestBookFile_List(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._book = 'book'
        # create a test file
        cls._width = 40
        pages = utility.test_book((cls._width, 8))

        cls._len = len(pages)

        with open(cls._book, 'wb') as fh:
            for page in pages:
                fh.write(bytearray(page))

        cls._bookfile = BookFile_List(cls._book, cls._width)

    def test_book_file_create(self):
        self.assertIsInstance(self._bookfile, BookFile_List)

    def test_book_file_len(self):
        self.assertEqual(len(self._bookfile), self._len)

    def test_book_file_content(self):
        w = self._width
        h = 8
        # test every page of the book
        for i in range(8):
            expected_pin = i + (i << 3)
            self.assertEqual(
                self._bookfile[i * h:i * h + 1][0], (expected_pin,) * w)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._book)
