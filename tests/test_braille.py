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

    def test_encodings(self):
        self.assertIn('braille-ascii', braille.BUILTIN_ENCODINGS)
        self.assertIn('euro-braille', braille.BUILTIN_ENCODINGS)
        self.assertEqual(braille.BUILTIN_ENCODINGS['euro-braille'].title, 'EuroBraille DE')
        self.assertEqual(
            braille.BUILTIN_ENCODINGS['braille-ascii'].title,
            'North American Braille ASCII'
        )
        self.assertEqual(list(braille.BUILTIN_ENCODINGS.keys()), ['braille-ascii', 'euro-braille'])

    def test_encoding_backwards_compatibility(self):
        # Stored state using EuroBraille or variants should resolve cleanly
        for name in ('euro-braille', 'EuroBraille', 'Eurobraille', 'EuroBraille DE',
                     'Eurobraille DE', 'euro-braille-de', 'eurobraille-de'):
            self.assertEqual(braille.resolve_encoding(name), 'euro-braille')
            self.assertIn(name, braille.BUILTIN_ENCODINGS)
            self.assertEqual(braille.BUILTIN_ENCODINGS[name].title, 'EuroBraille DE')
            self.assertEqual(braille.BUILTIN_ENCODINGS.get(name).title, 'EuroBraille DE')

        # ASCII variants
        for name in ('braille-ascii', 'North American Braille ASCII',
                     'north-american-braille-ascii'):
            self.assertEqual(braille.resolve_encoding(name), 'braille-ascii')

        # Fallback for unknown / None
        self.assertEqual(braille.resolve_encoding(None), braille.DEFAULT_ENCODING)
        self.assertEqual(braille.resolve_encoding('unknown-encoding'), braille.DEFAULT_ENCODING)

    def test_set_encoding(self):
        # Test switching between encodings
        braille.set_encoding('euro-braille')
        self.assertEqual(braille.mapping, braille.BUILTIN_ENCODINGS['euro-braille'].mapping)

        # Backwards compatible alias sets the same mapping
        braille.set_encoding('EuroBraille')
        self.assertEqual(braille.mapping, braille.BUILTIN_ENCODINGS['euro-braille'].mapping)

        # Reset to default
        braille.set_encoding('braille-ascii')
        self.assertEqual(braille.mapping, braille.BUILTIN_ENCODINGS['braille-ascii'].mapping)
