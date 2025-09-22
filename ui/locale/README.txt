Uses babel translation library.  To extract a POT file from the source, use
(from project root):

    pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui

This only needs to be done once for all languages - although will need to
be run after any set of code changes that add or change display text.

The `update-language.sh` script aims to find changes and auto translate and
transcribe them to braille.

    cd ui/locale
    . ve/bin/activate
    export DEEPL_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:xx
    ./update-language.sh en_GB 'EN-GB' en-ueb-g1.ctb 'English, UEB grade 1' en-ueb-g2.ctb 'English, UEB grade 2'
    ./update-language.sh de_DE DE de-g1-detailed.ctb 'Deutsch, G1' de-g2.ctb 'Deutsch, G2'
    ./update-language.sh fr_FR FR fr-bfu-comp6.utb 'Français, G1' fr-bfu-g2.ctb 'Français, G2'

(Note the `requirements-translate.txt` file can be used to create a locale
virtual environment for this - refer to INSTALL.md.)

The `update-language.sh` script has the following parameters:

    update-language.sh <language_country locale> <deepl language code> [<liblouis table> '<menu string>']+

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
     `canute.po` or it is marked with a `#, fuzzy` tag
   * only transcribes the translation back when there is no braille in the
     `canute.po` or it is marked with a `#, fuzzy` tag

The goal here is to allow manual tweaks to either the translation or the
transcribed files - and for these not to be overwritten.

If updating a translation manually in the `canute_translated` file, then make
sure to delete the `msgstr` in the `canute.po` file to make sure it gets
transcribed.

Sometimes the autotranscribed PO needs manual tweaks, like adjusting
inter-paragraph spacing so that paragraphs break across pages in sensible ways,
and removing formatting hints like AsciiDoc '<<<'.

If you make any such tweaks to an autotranslated PO, you must then separately
remake the corresponding MO, by re-running the update script.

To see tweaks applied in the past, check the git diff.
___

If you get the error `ModuleNotFoundError: No module named 'louis'` you may
need to run something like the following first:

    export PYTHONPATH="$(brew --prefix liblouis)/lib/python3.13/site-packages:$PYTHONPATH"

