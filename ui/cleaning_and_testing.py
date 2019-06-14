# A special book to show all faces of all rotors, allowing for a
# thorough wipe-down for cleaning while doubling as a crude way to check
# for hardware errors.
from .braille import unicode_to_pin_num
from .book.book_file import BookFile, LoadState

# There's no real use in having state for this book, but the special
# cases required to exclude it from state-keeping would cause more mess
# than they'd save.
cleaning_filename = '@@__cleaning_and_testing__@@'

NUM_ROWS = 9
NUM_COLS = 40


class CleaningAndTesting(BookFile):
    @property
    def title(self):
        return 'for cleaning and testing canute'

    @staticmethod
    def create():
        pages = []
        for pat in '⠉⠒⠤⠛⠶⠭⠿⠀':
            dots = unicode_to_pin_num(pat)
            pages.append(((dots,) * NUM_COLS,) * NUM_ROWS)
        pages = tuple(pages)
        return CleaningAndTesting(cleaning_filename, NUM_COLS, NUM_ROWS,
                                  pages=pages, load_state=LoadState.DONE)
