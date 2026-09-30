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


class TestLanguageMenuLabels(unittest.TestCase):
    def test_available_languages_loaded(self):
        from ui.i18n import available_languages
        languages = available_languages()
        self.assertIn('de_DE.UTF-8@de-g1-detailed', languages)
        self.assertIn('de_DE.UTF-8@de-g2', languages)

    def test_german_braille_labels_no_ueb(self):
        from ui.i18n import available_languages
        languages = available_languages()
        # Braille dots for 'ueb' (⠥⠑⠃) must not appear in German language labels
        ueb_braille = '⠥⠑⠃'
        g1_title = languages['de_DE.UTF-8@de-g1-detailed']
        g2_title = languages['de_DE.UTF-8@de-g2']

        self.assertNotIn(ueb_braille, g1_title)
        self.assertNotIn(ueb_braille, g2_title)

        # Expected Braille labels transcribed from 'Deutsch, G1' and 'Deutsch, G2'
        self.assertEqual(g1_title, '⠨⠙⠣⠞⠱⠂⠀⠘⠛⠼⠁')
        self.assertEqual(g2_title, '⠙⠱⠂⠀⠠⠛⠼⠃')
