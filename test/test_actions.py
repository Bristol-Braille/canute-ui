import unittest
import mock
import ui.actions as actions
from ui.initial_state import initial_state
import ui.utility as utility
from ui.bookfile_list import BookFile_List


initial = initial_state['app']


class TestActions(unittest.TestCase):
    def test_add_books(self):
        self.assertEqual(len(initial['books']), 0)
        r = actions.AppReducers()
        data = mock.MagicMock()
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['books']), 0)
        self.assertEqual(len(state['books']), 1)

    def test_add_books2(self):
        '''cannot add the same book twice'''
        self.assertEqual(len(initial['books']), 0)
        r = actions.AppReducers()
        data = mock.MagicMock()
        data.filename = 'test'
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['books']), 0)
        self.assertEqual(len(state['books']), 1)
        state = r.add_books(state, [data])
        self.assertEqual(len(initial['books']), 0)
        self.assertEqual(len(state['books']), 1)

    def test_remove_books(self):
        self.assertEqual(len(initial['books']), 0)
        r = actions.AppReducers()
        data = mock.MagicMock()
        data.filename = 'test'
        state = r.add_books(initial, [data])
        self.assertEqual(len(initial['books']), 0)
        self.assertEqual(len(state['books']), 1)
        state = r.remove_books(state, [data.filename])
        self.assertEqual(len(initial['books']), 0)
        self.assertEqual(len(state['books']), 0)

    def test_book_navigation(self):
        self.assertEqual(len(initial['books']), 0)
        r = actions.AppReducers()
        pages = utility.test_book((40, 9))
        with open('/tmp/book', 'w') as fh:
            for page in pages:
                fh.write(bytearray(page))

        bookfile = BookFile_List('/tmp/book', 40)
        state = r.add_books(initial, [bookfile])
        state = r.go_to_book(state, 0)

        self.assertEqual(state['location'], 0)
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
