import unittest
from ui.book.book_file import BookFile
from ui.book.handlers import init, read_pages, get_page_data

from .util import async_test


class TestBookFileBrf(unittest.TestCase):
    @classmethod
    @async_test
    async def setUpClass(self):
        self.filename = ('books/A_balance_between_technology_and_Braille_Addin'
                         + 'g_Value_and_Creating_a_Love_of_Reading.BRF')
        book = BookFile(self.filename, 40, 9)
        book = await init(book)
        self.book = await read_pages(book)

    def test_filename(self):
        self.assertEqual(self.book.filename, self.filename)

    def test_title(self):
        self.assertIsNotNone(self.book.title)

    def test_has_len(self):
        self.assertGreater(len(self.book.pages), 0)

    @async_test
    async def test_get_line(self):
        page = await get_page_data(self.book, None)
        self.assertIsNotNone(page[0])

    def test_page(self):
        self.assertEqual(self.book.page_number, 0)

    def test_bookmarks(self):
        self.assertIsNotNone(self.book.bookmarks)

    @classmethod
    def tearDownClass(self):
        pass


class TestBookFilePef(unittest.TestCase):
    @classmethod
    @async_test
    async def setUpClass(self):
        self.filename = "books/g2 AESOP'S FABLES.pef"
        book = BookFile(self.filename, 40, 9)
        book = await init(book)
        self.book = await read_pages(book)

    def test_filename(self):
        self.assertEqual(self.book.filename, self.filename)

    def test_title(self):
        self.assertIsNotNone(self.book.title)

    def test_has_len(self):
        self.assertGreater(len(self.book.pages), 0)

    @async_test
    async def test_get_line(self):
        page = await get_page_data(self.book, None)
        self.assertIsNotNone(page[0])

    def test_page_number(self):
        self.assertEqual(self.book.page_number, 0)

    def test_bookmarks(self):
        self.assertIsNotNone(self.book.bookmarks)

    @classmethod
    def tearDownClass(self):
        pass
