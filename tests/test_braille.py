import unittest
import os
import ui.braille as braille
import ui.utility as utility


dir_path = os.path.dirname(os.path.realpath(__file__))
test_books_dir = os.path.join(dir_path, 'test-books')


class TestBraille(unittest.TestCase):
    def setUp(self):
        pass

    def test_pin_num_to_unicode(self):
        for p in range(64):
            self.assertEqual(braille.unicode_to_pin_num(
                braille.pin_num_to_unicode(p)), p)

    def test_pin_num_to_alpha(self):
        for p in range(64):
            self.assertEqual(braille.alpha_to_pin_num(
                braille.pin_num_to_alpha(p)), p)

    def test_find_files(self):
        self.assertEqual(len(utility.find_files(test_books_dir, ('brf',))), 2)
        self.assertEqual(len(utility.find_files(test_books_dir, ('pef',))), 1)
        self.assertEqual(
            len(utility.find_files(test_books_dir, ('brf', 'pef'))),
            3
        )
