import unittest
import comms_codes as comms
from pageable import Menu, Book, Library
from utility import *
from driver_emulated import Emulated
from ConfigParser import ConfigParser
from bookfile_list import BookFile_List
import os
from driver_emulated import Emulated

class TestUtility(unittest.TestCase):

    def setUp(self):
        pass

    def test_pin_num_to_unicode(self):
        for p in range(64):
            self.assertEqual(unicode_to_pin_num(pin_num_to_unicode(p)), p)
            
    def test_pin_num_to_alpha(self):
        for p in range(64):
            self.assertEqual(alpha_to_pin_num(pin_num_to_alpha(p)), p)

class TestBookFile_List(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._book = 'book'
        # create a test file
        cls._dimensions = (28,4) #canute
        pages = test_book(cls._dimensions)

        with open(cls._book, 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        cls._bookfile = BookFile_List(cls._book, cls._dimensions)

    def test_book_file_create(self):
        self.assertIsInstance(self._bookfile, BookFile_List)

    def test_book_file_len(self):
        self.assertEqual(len(self._bookfile),8 * self._dimensions[1])

    def test_book_file_content(self):
        w = self._dimensions[0] 
        h = self._dimensions[1]
        # test every page of the book
        for i in range(8):
            expected_pin = i + (i << 3)
            self.assertEqual(self._bookfile[i*h:i*h+1][0], (expected_pin,) * w)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._book)

class TestPageable(unittest.TestCase):

    def setUp(self):
        pass

    @classmethod
    def setUpClass(cls):
        config = ConfigParser()
        config.read('config.rc')

        ui = None
        content = []
        dimensions = [20,4]
        cls.menu = Menu(dimensions, config, ui)

    def test_num_pages(self):
        self.assertEqual(self.menu.get_num_pages(), 1)

class TestDriverEmulated(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls._driver = Emulated()

    def test_rxtx_data(self):
        self._driver.send_data(comms.CMD_GET_CHARS)
        self.assertEqual(self._driver.get_data(None), Emulated.CHARS)

        self._driver.send_data(comms.CMD_GET_ROWS)
        self.assertEqual(self._driver.get_data(None), Emulated.ROWS)

        test_data = 0
        self._driver.send_data(comms.CMD_SEND_DATA, test_data)
        self.assertEqual(self._driver.get_data(None), test_data)

    @classmethod
    def tearDownClass(cls):
        cls._driver.__exit__(None, None, None)

class TestDriverPi(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
