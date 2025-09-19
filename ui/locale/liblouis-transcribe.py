
import argparse
import polib
import louis
import textwrap
from datetime import datetime, timezone

CANUTE_WIDTH = 40

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Translate .po files using liblouis")
parser.add_argument("-i", "--input", required=True, help="Path to the input language .po file")
parser.add_argument("-o", "--output", required=True, help="Path to the output braille .po file")
parser.add_argument("-t", "--table", required=True, help="Target braille table")
parser.add_argument("-n", "--name", required=True, help="Language and table name to use in menu")
args = parser.parse_args()

MENU_MSGID = 'Language Name, UEB grade'

# Only translate non braille translations - 0x2800-0x283F is 6-dot braille
# or any that have been fuzzy matched by msgmerge
def should_translate(entry):
    return 'fuzzy' in entry.flags or not all(0x2800 <= ord(c) <= 0x283f for c in entry.msgstr)

dest = polib.pofile(args.output)
src = polib.pofile(args.input)
valid_entries = [e for e in src if not e.obsolete]

dest.metadata = src.metadata

transcribed_count = 0
for src_entry in valid_entries:

    dest_entry = dest.find(src_entry.msgid)

    if should_translate(dest_entry):
        # we use double spaces (from \n + \n) as line break indicator
        if src_entry.msgid.find('  ') != -1:
            print('Warning: embedded double-space:\n' + str(src_entry.occurrences))

        if src_entry.msgid == MENU_MSGID:
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

        if 'fuzzy' in dest_entry.flags and 'fuzzy' not in src_entry.flags:
            dest_entry.flags.remove('fuzzy')

        transcribed_count += 1

if transcribed_count > 0:
    now = datetime.now(timezone.utc).strftime('%F %H:%M%z')
    dest.metadata['PO-Revision-Date'] = now

dest.save(args.output)
