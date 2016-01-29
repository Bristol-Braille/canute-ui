#!/usr/bin/env python
from multiprocessing import Process
import unittest
import comms_codes as comms
from pageable import Menu, Book, Library
from utility import *
from driver_emulated import Emulated
from driver_pi import Pi
from bookfile_list import BookFile_List
import os
import pty
import struct
import config_loader

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

class TestMenu(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = config_loader.load()

        ui = None
        dimensions = [20,4]
        cls._menu = Menu(dimensions, config, ui)

    def test_num_pages(self):
        self.assertEqual(self._menu.get_num_pages(), 1)

class TestBook(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config = config_loader.load()
        cls._bookfile = 'book'

        # create a test file
        cls._dimensions = (28,4) #canute
        pages = test_book(cls._dimensions)

        with open(cls._bookfile, 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        ui = None
        book_def = {"title": 'test',
                    "filename": cls._bookfile,
                    "type": 'native'}

        cls._book = Book(book_def, cls._dimensions, config, ui)

    def test_num_pages(self):
        self.assertEqual(self._book.get_num_pages(), 8)


    def test_navigation(self):
        self._book.home()
        self.assertEqual(self._book.page, 0)

        # edge case
        self._book.prev()
        self.assertEqual(self._book.page, 0)

        self._book.next()
        self.assertEqual(self._book.page, 1)

        self._book.end()
        self.assertEqual(self._book.page, 7)

        # edge case
        self._book.next()
        self.assertEqual(self._book.page, 7)

        self._book.prev()
        self.assertEqual(self._book.page, 6)

    def test_content(self):
        page_len = self._dimensions[0] * self._dimensions[1]
        # start at home
        self._book.home()
        self.assertEqual(self._book.page, 0)

        for i in range(8):
            data = self._book.show()
            expected_pin = i + (i << 3)
            self.assertEqual(data, [expected_pin] * page_len)
            self._book.next()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._bookfile)

class TestLibrary(unittest.TestCase):

    def create_book(self, name):
        # create a test file
        pages = test_book(self._dimensions)
        with open(name, 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        self._bookfiles.append(name)

    @classmethod
    def setUpClass(cls):
        cls._bookfiles = []
        cls._dimensions = (28,4) #canute
        config = config_loader.load()

        ui = None
        cls._lib = Library(cls._dimensions, config, ui)

    def test_navigation_when_empty(self):
        self._lib.home()
        self._lib.delete_content()
        self.assertEqual(self._lib.get_num_pages(), 0)

        self.assertEqual(self._lib.page, 0)
        self._lib.next()
        self.assertEqual(self._lib.page, 0)
        self._lib.prev()
        self.assertEqual(self._lib.page, 0)
        self._lib.end()
        self.assertEqual(self._lib.page, 0)
        self._lib.home()
        self.assertEqual(self._lib.page, 0)

    def test_add_new_pef_book(self):
        return

    def test_add_new_canute_book(self):
        self._lib.delete_content()
        book_name = 'aaa.canute'
        self.create_book(book_name)
        self._lib.add_book(book_name)
        self.assertEqual(self._lib.get_num_pages(), 1)

    def add_book_and_test(self, name, exp_pos, exp_len):
        w = self._dimensions[0]
        book_name = name + '.canute'
        self.create_book(book_name)
        self._lib.add_book(book_name)

        self.assertEqual(self._lib.get_num_pages(), exp_len)
        data = self._lib.show()
        self.assertEqual(data[w*exp_pos:w*exp_pos+3], alphas_to_pin_nums(name))

    def test_add_book_ordering(self):
        # start at home with no books
        self._lib.delete_content()
        self._lib.home()

        # add a bunch of books and check they go in the right order
        self.add_book_and_test('ggg', 0, 1)
        self.add_book_and_test('bbb', 0, 1)
        self.add_book_and_test('bbc', 1, 1)
        self.add_book_and_test('hhh', 3, 1)

        # overflow to next page
        self.add_book_and_test('hha', 3, 2)

        # check first book of 2nd page is the last one added
        self._lib.end()
        self.assertEqual(self._lib.show()[0:3], alphas_to_pin_nums('hhh'))

    @classmethod
    def tearDownClass(cls):
        for file in cls._bookfiles:
            os.unlink(file)

class TestDriverEmulated(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if "TRAVIS" in os.environ:
            raise unittest.SkipTest("Skip Tkinter tests on TRAVIS")
        cls._driver = Emulated()

    def test_rxtx_data(self):
        self._driver.send_data(comms.CMD_GET_CHARS)
        self.assertEqual(self._driver.get_data(None), Emulated.CHARS)

        self._driver.send_data(comms.CMD_GET_ROWS)
        self.assertEqual(self._driver.get_data(None), Emulated.ROWS)

        self._driver.send_data(comms.CMD_SEND_DATA)
        self.assertEqual(self._driver.get_data(None), 0)

    def test_rxtx_row(self):
        self._driver.send_data(comms.CMD_SEND_ROW)
        self.assertEqual(self._driver.get_data(None), 0)

    @classmethod
    def tearDownClass(cls):
        cls._driver.__exit__(None, None, None)


class TestDriverPi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        cls._master = master
        cls._driver = Process(target=Pi, args=(s_name, False))
        cls._driver.start()

    def get_message(self, len=1):
        message = os.read(self._master,1)
        data = struct.unpack('1b', message)
        return data

    def send_message(self, data, cmd):
        message = struct.pack('%sb' % (len(data) + 1), cmd, *data)
        os.write(self._master, message)

    def test_rxtx_data(self):
        # receive the get chars message
        self.assertEqual(self.get_message()[0], comms.CMD_GET_CHARS)

        # send chars
        self.send_message([24], comms.CMD_GET_CHARS)

        # receive the get rows message
        self.assertEqual(self.get_message()[0], comms.CMD_GET_ROWS)

        # send rows
        self.send_message([4], comms.CMD_GET_ROWS)

    @classmethod
    def tearDownClass(cls):
        cls._driver.join()


if __name__ == '__main__':
    unittest.main()
