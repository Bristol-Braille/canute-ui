import unittest
import mock

import ui.actions as actions
from ui.library.reducers import LibraryReducers
from ui.initial_state import initial_state
from ui.book_file import BookFile

initial = initial_state['app']


class TestActions(unittest.TestCase):
    def test_add_books(self):
        self.assertEqual(len(initial['user']['books']), 1)
        r = LibraryReducers()
        data = mock.MagicMock()
        data.title = 'foo'
        data.filename = 'foo'
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['user']['books']), 1)
        self.assertEqual(len(state['user']['books']), 2)

    def test_add_books2(self):
        '''cannot add the same book twice'''
        self.assertEqual(len(initial['user']['books']), 1)
        r = LibraryReducers()
        data = mock.MagicMock()
        data.filename = 'test'
        data.title = 'test'
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['user']['books']), 1)
        self.assertEqual(len(state['user']['books']), 2)
        state = r.add_books(state, [data])
        self.assertEqual(len(initial['user']['books']), 1)
        self.assertEqual(len(state['user']['books']), 2)

    def test_remove_books(self):
        self.assertEqual(len(initial['user']['books']), 1)
        r = LibraryReducers()
        data = mock.MagicMock()
        data.filename = 'test'
        data.title = 'test'
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['user']['books']), 1)
        self.assertEqual(len(state['user']['books']), 2)
        state = r.remove_books(state, [data.filename])
        self.assertEqual(len(initial['user']['books']), 1)
        self.assertEqual(len(state['user']['books']), 1)

    def test_book_navigation(self):
        self.assertEqual(len(initial['user']['books']), 1)
        ra = actions.AppReducers()
        rl = LibraryReducers()
        filename = ('books/A_balance_between_technology_and_Braille_Addin'
                    + 'g_Value_and_Creating_a_Love_of_Reading.BRF')
        bookfile = BookFile(filename, 40, 9)
        state = rl.add_books(initial, [bookfile])
        state = rl.go_to_book(state, 0)

        self.assertEqual(state['location'], 'book')
        self.assertEqual(state['user']['books'][0].page_number, 0)

        # check we can't go backwards from page 0
        state = ra.previous_page(state, None)
        self.assertEqual(state['user']['books'][0].page_number, 0)

        # check we can go forwards from page 0
        state = ra.next_page(state, None)
        self.assertEqual(state['user']['books'][0].page_number, 1)

        # go fowards too many times
        for i in range(10):
            state = ra.next_page(state, None)

        # and check we're on the last page
        self.assertEqual(state['user']['books'][0].page_number, 11)
