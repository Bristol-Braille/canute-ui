import unittest
import os
import ui.comms_codes as comms
if 'TRAVIS' not in os.environ:
    from ui.driver_emulated import Emulated


class TestDriverEmulated(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if 'TRAVIS' in os.environ:
            raise unittest.SkipTest('Skip emulated driver tests on TRAVIS')
        else:
            cls._driver = Emulated()

    def test_rxtx_data(self):
        self._driver.send_data(comms.CMD_GET_CHARS)
        self.assertEqual(self._driver.get_data(None), Emulated.CHARS)

        self._driver.send_data(comms.CMD_GET_ROWS)
        self.assertEqual(self._driver.get_data(None), Emulated.ROWS)

        self._driver.send_data(comms.CMD_SEND_PAGE)
        self.assertEqual(self._driver.get_data(None), 0)

    def test_rxtx_row(self):
        self._driver.send_data(comms.CMD_SEND_LINE)
        self.assertEqual(self._driver.get_data(None), 0)

    @classmethod
    def tearDownClass(cls):
        cls._driver.__exit__(None, None, None)
