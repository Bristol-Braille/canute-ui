import unittest
import os
import math
import ui.utility as utility
import ui.braille as braille
import ui.convert as convert
from ui.bookfile_list import BookFile_List


dir_path = os.path.dirname(os.path.realpath(__file__))
test_books_dir = os.path.join(dir_path, 'test-books')


class TestConvert(unittest.TestCase):
    def test_convert_brf_breaks(self):
        book_name = 'brf_break_test'
        brf_file = os.path.join(test_books_dir, book_name + '.brf')
        native_file = os.path.join(test_books_dir, book_name + '.canute')
        convert.convert_brf(40, 4, brf_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)
        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 4)

    def test_convert_pef(self):
        book_name = 'pef_test'
        pef_file = os.path.join(test_books_dir, book_name + '.pef')
        native_file = os.path.join(test_books_dir, book_name + '.canute')
        convert.convert_pef(40, 4, pef_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)
        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 25)
        content = content[0:40]
        content = utility.flatten(content)
        alphas = braille.pin_nums_to_alphas(content)
        alphas = ''.join(alphas).lower()
        self.assertEqual(
            alphas[0:40], 'the quickbrownfoxjumpedoverlazydog.000  ')

    def test_convert_brf(self):
        book_name = 'brf_test'
        brf_file = os.path.join(test_books_dir, book_name + '.BRF')
        native_file = os.path.join(test_books_dir, book_name + '.canute')
        convert.convert_brf(40, 4, brf_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)

        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 248)
        content = utility.flatten(content[0:4])

        alphas = braille.pin_nums_to_alphas(content)
        alphas = ''.join(alphas).lower()

        with open(brf_file) as fh:
            lines = fh.readlines()

        # just test first 4 lines
        brf_content = ''
        for line in lines[0:4]:
            # pad the line to be the same as width
            line = line.strip()
            line += ' ' * (40 - len(line))
            brf_content += line

        self.assertEqual(alphas, brf_content)
