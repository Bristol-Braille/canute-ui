import unittest
import os
from . import utility
from ui.book import Book

class TestBookBrf(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.filename = 'books/A_balance_between_technology_and_Braille_Adding_Value_and_Creating_a_Love_of_Reading.BRF'
        self.book = Book(self.filename, 40)

    def test_filename(self):
        self.assertEqual(self.book.filename, self.filename)

    def test_title(self):
        self.assertIsNotNone(self.book.title)

    def test_has_len(self):
        self.assertGreater(len(self.book), 0)

    def test_get_line(self):
        self.assertIsNotNone(self.book[0])



    @classmethod
    def tearDownClass(self):
        pass
