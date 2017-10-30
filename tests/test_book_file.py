import unittest
from ui.book_file import BookFile


class TestBookFileBrf(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.filename = ('books/A_balance_between_technology_and_Braille_Addin'
                         + 'g_Value_and_Creating_a_Love_of_Reading.BRF')
        self.book = BookFile(self.filename, 40)

    def test_filename(self):
        self.assertEqual(self.book.filename, self.filename)

    def test_title(self):
        self.assertIsNotNone(self.book.title)

    def test_has_len(self):
        self.assertGreater(len(self.book), 0)

    def test_get_line(self):
        self.assertIsNotNone(self.book[0])

    def test_page(self):
        self.assertEqual(self.book.page, 0)

    def test_bookmarks(self):
        self.assertIsNotNone(self.book.bookmarks)

    @classmethod
    def tearDownClass(self):
        pass


class TestBookFilePef(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.filename = ("books/g2 AESOP'S FABLES.pef")
        self.book = BookFile(self.filename, 40)

    def test_filename(self):
        self.assertEqual(self.book.filename, self.filename)

    def test_title(self):
        self.assertIsNotNone(self.book.title)

    def test_has_len(self):
        self.assertGreater(len(self.book), 0)

    def test_get_line(self):
        self.assertIsNotNone(self.book[0])

    def test_page(self):
        self.assertEqual(self.book.page, 0)

    def test_bookmarks(self):
        self.assertIsNotNone(self.book.bookmarks)

    @classmethod
    def tearDownClass(self):
        pass
