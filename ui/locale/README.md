# Translations

## Setup

Create a local vitual environment using the translation requirements file
something like:

```
cd ui/locale
python3.13 -m venv ve
. ve/bin/activate
pip3 install -r requirements-translate.txt
```

On macOS you will also need `liblouis`

```
brew install liblouis
export PYTHONPATH="$(brew --prefix liblouis)/lib/python3.13/site-packages:$PYTHONPATH"
```

(Without the environment variable you may get
`ModuleNotFoundError: No module named 'louis'` errors)

## Translations

To extract a translation template POT file from the source, use (from project root):

```
pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui
```

This only needs to be done once for all languages - although will need to
be run after any set of code changes that add or change display text.

The `update-language.sh` script aims to find changes and auto translate and
transcribe them to braille.

```
cd ui/locale
. ve/bin/activate
export DEEPL_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xx
./update-language.sh fr_FR FR fr-bfu-comp6.utb 'Français, G1' fr-bfu-g2.ctb 'Français, G2'
```

The `update-language.sh` script has the following parameters:

```
update-language.sh [-f] <language_country locale> <deepl language code> [<liblouis table> '<menu string>']+
```

For each locale the script will:

   1. create or update the locale's `LC_MESSAGES/canute.po` with strings
      from the common template `canute.pot` file
   2. create or update the locale's
      `LC_MESSAGES/canute_translated_<language-code>.po` with translations of
      any new/changed English strings in the canute.po using the DeepL
      translation API
   3. transcribe these new or changed translations back into the `canute.po`
      file as unicode Braille using the liblouis conversion table
   4. compile these files into the `canute.po` which is used by the application

Note that this process only:

   * adds translations when there is no braille transcription in the
     `canute.po`, an empty translation in the `canute_translated` file
     or it is marked with a `#, fuzzy` tag
   * only transcribes the translation back when there is no braille in the
     `canute.po` or it is marked with a `#, fuzzy` tag, or the `-f` flag
     is given

The goal here is to allow manual tweaks to either the translation or the
transcribed files - and for these not to be overwritten unless requested.

Sometimes the autotranscribed PO needs manual tweaks, like adjusting
inter-paragraph spacing so that paragraphs break across pages in sensible ways,
and removing formatting hints like AsciiDoc '<<<'.

If you make any such tweaks to an autotranslated PO, you must then separately
remake the corresponding MO, by re-running the update script.

To see tweaks applied in the past, check the git diff.

## Workflows

Use the following guides for adding or updating translations:

   1. Add translations for a new language
   2. Update a language translation
   3. Tweak a Braille transcription
   4. Make translations for a code change

### Add Translations for a new language

First you will need:

   * the language and country [locale name](https://www.gnu.org/software/gettext/manual/html_node/Locale-Names.html)
   * the DeepL [language code](https://developers.deepl.com/docs/getting-started/supported-languages)

for the language. And then:

   * the [liblouis table](https://github.com/liblouis/liblouis/tree/master/tables)
   * and the _local name_ of the language, and what grade it is (for display in the menu)

for each uncontracted/contracted transcription you wish to add.

Then run the update-language script

```
./update-language.sh <locale name> <language code> <liblouis table> '<local name, grade 1>' <liblouis table> '<local name, grade 2>'
```

This will create two `<locale name>.UTF-8@<liblouis table>/LC_MESSAGES` folders
with three files in that you should add to git.

Add the `./update-language.sh` command for the language to the `update-all.sh`
script.


### Update a Language Translation

The `canute_translated_<lang>.po` file can be sent to third-parties to update
with better/more suitable language translations.

If the file does not contain the messages that you would like translating, the
`canute.pot` template file can be used instead.  Alternatively, individual
messages can be copy/pasted from the template if only a few sections need
attention.

Once updated translations have been received update the
`canute_translated_<lang>.po` file - this would usually be done for all
Braille grades.

Run the update language with `-f` flag as the first parameter - this will
ensure that all new translations are transcribed into Braille in the
`canute.po` file:

```
./update-language.sh -f <locale name> <language code> <liblouis table> '<local name, grade 1>' <liblouis table> '<local name, grade 2>'
```

Check the changes using `git diff` or similar and commit them.


### Tweak a Braille Transcription

If the Braille itself needs adjusting - e.g. to place page breaks in better
locations - this can be done by editing the appropriate `canute.po` files.

Run the `update-language.sh` script (without the `-f`) to compile a new
`canute.mo` file.

As long as the new Braille content uses the unicode character set - including
the Braille space character '⠀' - then it will not get updated in future runs
unless the `-f` flag is used.


### Make Translations for a Code Change

After making code changes that need new translations, for example due to adding
a new menu item or changing help text, run the `update-all.sh` script.

This runs the `pybabel extract` command from the root of the repository to
update the `canute.pot` template file.

Then `update-language.sh` calls are made for each of the languages.  Any new
or changed strings will be added to the language's `canute.po` and then
auto-translated (where possible) into the `canute_translated` files before
being transcribed back into the `canute.po` and compiled into the `canute.mo`.

After any change like this it is important to check the git diff before
committing the changes.  In particular, it is important to watch out for
fuzzy matched translations (which have changed only slightly) to ensure they
are still accurate.  The `#, fuzzy` comments, along with the original 'before'
msgid may be removed once checked and committed.
