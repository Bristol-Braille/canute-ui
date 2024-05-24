Uses babel translation library.  To extract a POT file from the source, use
(from project root):

pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui

The eventual goal is to maintain PO files on Transifex (we have an account) but
currently translations are done with `liblouis`, a little automation code, and
possibly some small manual tweaks.

To compile the resulting POT file into a set of useable MO files, use:

    cd ui/locale
    ./autotranslate.py

(Note the `requirements-translate.txt` file can be used to create a locale
virtual environment for this - refer to INSTALL.md.)

This generates a PO for each braille code from the POT using `liblouis`, then
compiles each PO to a MO.  Sometimes the autotranslated PO needs manual tweaks,
like adjusting inter-paragraph spacing so that paragraphs break across pages in
sensible ways, and removing formatting hints like AsciiDoc '<<<'.  If you make
any such tweaks to an autotranslated PO, you must then separately remake the
corresponding MO, e.g.:

    pybabel compile -f -D canute -d . -l en_GB.UTF-8@ueb1 -i en_GB.UTF-8@ueb1/LC_MESSAGES/canute.po
    pybabel compile -f -D canute -d . -l en_GB.UTF-8@ueb2 -i en_GB.UTF-8@ueb2/LC_MESSAGES/canute.po
    pybabel compile -f -D canute -d . -l de_DE.UTF-8@ueb1 -i de_DE.UTF-8@ueb1/LC_MESSAGES/canute.po
    pybabel compile -f -D canute -d . -l de_DE.UTF-8@ueb2 -i de_DE.UTF-8@ueb2/LC_MESSAGES/canute.po

To see tweaks applied in the past, check the git diff.
___

If you get the error `ModuleNotFoundError: No module named 'louis'` you may
need to run something like the following first:

    export PYTHONPATH="$(brew --prefix liblouis)/lib/python3.12/site-packages:$PYTHONPATH"

