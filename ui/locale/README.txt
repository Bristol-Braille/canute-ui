Uses babel translation library.  To generate POT file, use from root:

pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui

PO files are created with: https://www.transifex.com/bristol-braille-technology/canute/translate

To compile the resulting PO file into a useable MO file, use (for example):

mkdir -p ./locale/es_MX/LC_MESSAGES
pybabel compile -f -D canute -d ./ui/locale -l es_MX -i ./ui/locale/canute_es_MX.po
