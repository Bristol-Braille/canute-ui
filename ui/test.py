#!/usr/bin/env python
from multiprocessing import Process
from frozendict import frozendict
import unittest
import os
import pty
import struct
import math
import mock

from bookfile_list import BookFile_List
from driver_pi import Pi
from setup_logs import setup_logs
import utility
import comms_codes as comms
import config_loader
import convert
import actions
from initial_state import initial_state
from main import sync_library
if "TRAVIS" not in os.environ:
    from driver_emulated import Emulated

class TestUtility(unittest.TestCase):

    def setUp(self):
        pass

    def test_pin_num_to_unicode(self):
        for p in range(64):
            self.assertEqual(utility.unicode_to_pin_num(utility.pin_num_to_unicode(p)), p)

    def test_pin_num_to_alpha(self):
        for p in range(64):
            self.assertEqual(utility.alpha_to_pin_num(utility.pin_num_to_alpha(p)), p)

    def test_find_files(self):
        self.assertEqual(len(utility.find_files('../test-books', ('brf',))), 2)
        self.assertEqual(len(utility.find_files('../test-books', ('pef',))), 1)
        self.assertEqual(len(utility.find_files('../test-books', ('brf','pef'))), 3)


class TestBookFile_List(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._book = 'book'
        # create a test file
        cls._width = 40
        pages = utility.test_book((cls._width, 8))

        cls._len = len(pages)

        with open(cls._book, 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        cls._bookfile = BookFile_List(cls._book, cls._width)

    def test_book_file_create(self):
        self.assertIsInstance(self._bookfile, BookFile_List)

    def test_book_file_len(self):
        self.assertEqual(len(self._bookfile), self._len)

    def test_book_file_content(self):
        w = self._width
        h = 8
        # test every page of the book
        for i in range(8):
            expected_pin = i + (i << 3)
            self.assertEqual(self._bookfile[i*h:i*h+1][0], (expected_pin,) * w)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._book)


class TestDriverEmulated(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "TRAVIS" in os.environ:
            raise unittest.SkipTest("Skip emulated driver tests on TRAVIS")
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


class TestConvert(unittest.TestCase):
    def test_convert_brf_breaks(self):
        book_name = 'brf_break_test'
        book_path = '../test-books/'
        brf_file = book_path + book_name + '.brf'
        native_file = book_path + book_name + '.canute'
        convert.convert_brf(40, 4, brf_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)
        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 4)

    def test_convert_pef(self):
        book_name = 'pef_test'
        book_path = '../test-books/'
        pef_file = book_path + book_name + '.pef'
        native_file = book_path + book_name + '.canute'
        convert.convert_pef(40, 4, pef_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)
        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 25)
        content = content[0:40]
        content = utility.flatten(content)
        alphas = utility.pin_nums_to_alphas(content)
        alphas = ''.join(alphas).lower()
        self.assertEqual(alphas[0:40], 'the quickbrownfoxjumpedoverlazydog.000  ')

    def test_convert_brf(self):
        book_name = 'brf_test'
        book_path = '../test-books/'
        brf_file = book_path + book_name + '.BRF'
        native_file = book_path + book_name + '.canute'
        convert.convert_brf(40, 4, brf_file, native_file, remove=False)
        content = BookFile_List(native_file, 40)

        lines = len(content)
        pages = math.ceil(lines / 4.0)
        self.assertEqual(pages, 248)
        content = utility.flatten(content[0:4])

        alphas = utility.pin_nums_to_alphas(content)
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


class TestActions(unittest.TestCase):
    def test_add_books(self):
        self.assertEqual(len(initial_state['books']), 0)
        r = actions.Reducers()
        data = mock.MagicMock()
        state = r.add_books(initial_state, [data])
        self.assertEqual(len(initial_state['books']), 0)
        self.assertEqual(len(state['books']), 1)
    def test_add_books2(self):
        '''cannot add the same book twice'''
        self.assertEqual(len(initial_state['books']), 0)
        r = actions.Reducers()
        data = mock.MagicMock()
        data.filename = 'test'
        state = r.add_books(initial_state, [data])
        self.assertEqual(len(initial_state['books']), 0)
        self.assertEqual(len(state['books']), 1)
        state = r.add_books(state, [data])
        self.assertEqual(len(initial_state['books']), 0)
        self.assertEqual(len(state['books']), 1)
    def test_remove_books(self):
        self.assertEqual(len(initial_state['books']), 0)
        r = actions.Reducers()
        data = mock.MagicMock()
        data.filename = 'test'
        state = r.add_books(initial_state, [data])
        self.assertEqual(len(initial_state['books']), 0)
        self.assertEqual(len(state['books']), 1)
        state = r.remove_books(state, [data.filename])
        self.assertEqual(len(initial_state['books']), 0)
        self.assertEqual(len(state['books']), 0)

    def test_book_navigation(self):
        self.assertEqual(len(initial_state['books']), 0)
        r = actions.Reducers()
        pages = utility.test_book((40, 9))
        with open('/tmp/book', 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        bookfile = BookFile_List('/tmp/book', 40)
        state = r.add_books(initial_state, [bookfile])
        state = r.go_to_book(state, 0)

        self.assertEqual(state['app']['location'], 0)
        self.assertEqual(state['books'][0]['page'], 0)

        # check we can't go backwards from page 0
        state = r.previous_page(state, None)
        self.assertEqual(state['books'][0]['page'], 0)

        # check we can go forwards from page 0
        state = r.next_page(state, None)
        self.assertEqual(state['books'][0]['page'], 1)

        # go fowards too many times
        for i in range(10):
            state = r.next_page(state, None)

        # and check we're on the last page
        self.assertEqual(state['books'][0]['page'], 7)

if __name__ == '__main__':
    config = config_loader.load()
    config.read('config-test.rc')
    try:
        os.mkdir(config.get('files', 'library_dir'))
    except OSError:
        pass
    import logging
    setup_logs(config, logging.ERROR)
    unittest.main()
