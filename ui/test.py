import unittest
from pageable import Menu, Book, Library
from driver_emulated import Emulated
from ConfigParser import ConfigParser

class TestUtility(unittest.TestCase):

    def setUp(self):
        pass

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

if __name__ == '__main__':
    unittest.main()
