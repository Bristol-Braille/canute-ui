

# https://nasiothemes.com/2-ways-to-automatically-translate-po-files-for-free/
# pip install polib deepl
# python deepl-translate.py -f de_DE.po -l de

import os
import time
from datetime import datetime, timezone
import os.path
import argparse
import polib
import deepl

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Translate .po files using DeepL")
parser.add_argument("-i", "--input", required=True, help="Path to the .po file")
parser.add_argument("-o", "--output", required=True, help="Path to the translated .po file")
parser.add_argument("-l", "--lang", required=True, help="Target language code")
args = parser.parse_args()

lang = args.lang.upper()  # Convert to uppercase

# DeepL API Key
AUTH_KEY = os.environ.get('DEEPL_API_KEY') 
translator = deepl.Translator(AUTH_KEY)

# Only translate non braille translations - 0x2800-0x283F is 6-dot braille
# or any that have been fuzzy matched by msgmerge
def should_translate(entry):
    return 'fuzzy' in entry.flags or not all(0x2800 <= ord(c) <= 0x283f or c == '\n' for c in entry.msgstr)

# Load the .po files
src = polib.pofile(args.input)
if os.path.isfile(args.output):
    dest = polib.pofile(args.output)
else:
    dest = polib.POFile()
    dest.metadata = src.metadata

total_entries = len([entry for entry in src if entry.msgid and should_translate(entry)])
translated_count = 0

# Translate entries with progress
for i, entry in enumerate(src):
    if entry.msgid and should_translate(entry):
        dest_entry = dest.find(entry.msgid)

        if dest_entry is None and 'fuzzy' in entry.flags:
            dest_entry = dest.find(entry.previous_msgid)

        if dest_entry is None:
            dest_entry = entry
            dest.append(dest_entry)
        else:
            dest_entry.merge(entry)

        try:
            translation = translator.translate_text(entry.msgid, target_lang=lang)
            dest_entry.msgstr = translation.text
            translated_count += 1
            percent_done = (translated_count / total_entries) * 100
            print(f"Progress: {translated_count}/{total_entries} ({percent_done:.2f}%)", end="\r")
            time.sleep(0.1)  # Optional delay to avoid hitting API limits
        except Exception as e:
            print(f"\nError translating '{entry.msgid}': {e}")

# Save the translated .po file
if translated_count > 0:
    now = datetime.now(timezone.utc).strftime('%F %H:%M%z')
    dest.metadata['PO-Revision-Date'] = now

dest.save(args.output)

print(f"\nTranslation completed: {args.output}") 