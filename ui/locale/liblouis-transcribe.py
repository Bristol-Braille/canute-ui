
import os
import argparse
import polib
import time
import louis
import textwrap
from datetime import datetime, timezone

CANUTE_WIDTH = 40

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Translate .po files using liblouis")
parser.add_argument("-f", "--file", required=True, help="Path to the language .po file")
parser.add_argument("-t", "--table", required=True, help="Target braille table")
parser.add_argument("-n", "--name", required=True, help="Language and table name to use in menu")
args = parser.parse_args()

po_file = args.file
src = polib.pofile(po_file)
valid_entries = [e for e in src if not e.obsolete]

dest = polib.POFile()

dest.metadata = src.metadata
now = datetime.now(timezone.utc).strftime('%F %H:%M%z')
dest.metadata['PO-Revision-Date'] = now

for src_entry in valid_entries:
    # we use double spaces (from \n + \n) as line break indicator
    if src_entry.msgid.find('  ') != -1:
        print('Warning: embedded double-space:\n' +
                str(src_entry.occurrences))
    if src_entry.msgid == 'Language Name, UEB grade':
        msgstr = args.name
    else:
        msgstr = src_entry.msgstr

    translation = louis.translateString(
        ['unicode.dis', args.table],
        msgstr
    )

    # normalise to use ascii spaces for textwrap's benefit
    # note the first parameter below is a braille space!
    translation = translation.replace('⠀', ' ')

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
    # convert back to braille spaces
    wrapped = wrapped.replace(' ', '⠀')
    dest_entry = polib.POEntry(
        msgid=src_entry.msgid,
    )
    dest_entry.merge(src_entry)
    dest_entry.msgstr = wrapped
    dest.append(dest_entry)

destdir = os.path.dirname(po_file)
po_path = os.path.join(destdir, 'canute.po')
dest.save(po_path)
print(po_path)
mo_path = os.path.join(destdir, 'canute.mo')
dest.save_as_mofile(mo_path)
print(mo_path)
