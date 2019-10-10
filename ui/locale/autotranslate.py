#!/usr/bin/python3
#
# Do a naive, likely one-off automated translation from English print to
# the built-in supported English Braille variants.
#
# Don't forget to update the POT first.
#
import collections
import textwrap
import os
import polib
import louis
from datetime import datetime, timezone

print('''\
This OVERWRITES any existing translations with new automatic ones.
(By the time that matters, you shouldn't be using this any more.)
So be careful before committing changed translations!\
''')

CANUTE_WIDTH = 40

src = polib.pofile('canute.pot')
valid_entries = [e for e in src if not e.obsolete]

Variant = collections.namedtuple('Variant', ['name', 'table', 'locale'])

variants = [
    # Modifiers on the ISO 15897 locale codes are invented here.  That
    # system doesn't really allow for Braille.  Since this applies
    # solely to menu and help text I doubt there's enough material to
    # allow anyone to spot a difference between UEB and SEB.
    # We're somewhat beholden to Python's curious normalisation/aliasing
    # rules here:
    #   >> locale.normalize('en@UEB1')
    #   =>'en_US.ISO8859-1@ueb1'
    #   >> locale.normalize('en.UTF-8@UEB1')
    #   => 'en_US.UTF-8@ueb1'
    # The names are just unused suggestions for menu options.
    # It's assumed that the current system text uses British English
    # spellings and idioms; perhaps, again, there's not enough material
    # that anyone would notice.
    Variant('British English, UEB grade 1', 'en-ueb-g1.ctb', 'en_GB.UTF-8@ueb1'),
    Variant('British English, UEB grade 2', 'en-ueb-g2.ctb', 'en_GB.UTF-8@ueb2'),
]

for variant in variants:
    dest = polib.POFile()

    dest.metadata = src.metadata
    now = datetime.now(timezone.utc).strftime('%F %H:%M%z')
    dest.metadata['PO-Revision-Date'] = now

    for src_entry in valid_entries:
        # unicode.dis still uses ASCII spaces.
        if src_entry.msgid.find('  ') != -1:
            print('Warning: embedded double-space:\n' + str(src_entry.occurrences))
        translation = louis.translateString(
            ['unicode.dis', variant.table],
            src_entry.msgid
        )
        # Louis squashes newlines into spaces.  Provided there are
        # no double-spaces in the input we can assume a double-space
        # in the output was meant to be a line break.
        import re
        wrapped = []
        for para in re.split(r'  ', translation):
            wrapped.append(textwrap.fill(para, width=CANUTE_WIDTH))
            wrapped.append('\n')
            wrapped.append('\n')
        wrapped.pop()
        wrapped.pop()
        # At this point we could apply a general rule that no page
        # should ever start with a blank line; would save a manual tweak
        # or two.
        wrapped = ''.join(wrapped)
        dest_entry = polib.POEntry(
            msgid=src_entry.msgid,
        )
        dest_entry.merge(src_entry)
        dest_entry.msgstr = wrapped
        if dest_entry.msgid == 'English, UEB grade 1':
            dest_entry.msgstr = '⠠⠑⠝⠛⠇⠊⠎⠓⠂ ⠠⠠⠥⠑⠃ ⠛⠗⠁⠙⠑ ⠼⠁'
        elif dest_entry.msgid == 'English, UEB grade 2':
            dest_entry.msgstr = '⠠⠢⠛⠇⠊⠩⠂ ⠠⠠⠥⠑⠃ ⠛⠗⠁⠙⠑ ⠼⠃'
        dest.append(dest_entry)

    destdir = os.path.join(variant.locale, 'LC_MESSAGES')
    os.makedirs(destdir, exist_ok=True)
    po_path = os.path.join(destdir, 'canute.po')
    dest.save(po_path)
    print(po_path)
    mo_path = os.path.join(destdir, 'canute.mo')
    dest.save_as_mofile(mo_path)
    print(mo_path)
