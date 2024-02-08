from .braille import from_unicode
from .book.book_file import BookFile, LoadState

# This is no longer any kind of manual.
#
# The long-standing intention is that Canute ships with the full manual;
# it's an accident that the quick start got baked in.  For now, since
# the (nominal) manual is special in several ways and removal would
# cause code churn, the quick start has been replaced with this
# placeholder.  In time we'll kill this off completely and put permanent
# books on the Pi SD as regular BRFs.  For now, full manual will come on
# the library card and user will just have to be careful not to delete
# it.

manual_filename = '@@__canute_manual__@@'


def batch(a, n=9):
    return [a[i:i + n] for i in range(0, len(a), n)]


class Manual(BookFile):
    @property
    def title(self):
        # Since book titles are naively mapped from ASCII and since we
        # can only do that to SimBraille (currently!) the menu renderers
        # expect them in SimBraille.  So, I figure it's better to give a
        # naive-but-consistent SimBraille title here than a
        # decently-translated-but-inconsistent Unicode title.
        return 'Canute 360 by Bristol Braille'

    @staticmethod
    def create():
        text = _('''\
Canute 360 by Bristol Braille Technology

Bristol Braille Technology is a not-for-profit organisation dedicated \
to serving the Braille reading community.

Founded in 2011. Registered in the United Kingdom with the Regulator \
of Community Interest Companies. Company number 7518101.
''')
        lines = text.split('\n')
        pages = batch(lines)
        pages = tuple(tuple(from_unicode(line) for line in page)
                      for page in pages)
        return Manual(manual_filename, 40, 9, pages=pages, load_state=LoadState.DONE)

    def relpath(self):
        return self.filename
