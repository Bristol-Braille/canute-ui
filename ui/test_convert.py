import unittest
import logging
log = logging.getLogger(__name__)
import convert
from bookfile_list import BookFile_List
import math
import logging
import config_loader
import os
from setup_logs import setup_logs
import utility

class TestConvert(unittest.TestCase):
    def test_convert_brf_breaks(self):
        book_name = 'brf_break_test'
        book_path = '../test-books/'
        brf_file = book_path + book_name + '.brf'
        native_file = book_path + book_name + '.canute'
        convert.convert_brf(40, 4, brf_file, native_file, remove=False)
        book = BookFile_List(native_file, [40, 4])
        lines = len(book)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 4)

    def test_convert_pef(self):
        book_name = 'pef_test'
        book_path = '../test-books/'
        pef_file = book_path + book_name + '.pef'
        native_file = book_path + book_name + '.canute'
        convert.convert_pef(40, 4, pef_file, native_file, remove=False)
        content = BookFile_List(native_file, [40, 4])
        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 25)
        content = content[0:40]
        content = utility.flatten(content)
        alphas = utility.pin_nums_to_alphas(content)
        alphas = ''.join(alphas).lower()
        self.assertEqual(alphas[0:40], 'the quickbrownfoxjumpedoverlazydog.000  ')

if __name__ == '__main__':
    config = config_loader.load()
    config.read('config-test.rc')
    setup_logs(config, logging.ERROR)
    unittest.main()
