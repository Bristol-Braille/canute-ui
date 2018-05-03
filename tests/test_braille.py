import unittest
import ui.braille as braille

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

    def test_truncate_middle(self):
        inp = '123456789abcdefghi'
        width = 9
        truncated = braille.truncate_middle(inp, width)
        self.assertEqual(len(truncated), width)
