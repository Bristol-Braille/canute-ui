#!/usr/bin/env bash

locale_dir="$PWD/${BASH_SOURCE%/*}"

if [ "$1" == "-f" ]; then
   force_transcribe="-f"
   shift
fi

# language and country code, such as en_GB, de_DE or fr_FR
lang_code=$1
shift
# deepl language code such as EN-GB, DE or FR
# see https://developers.deepl.com/docs/getting-started/supported-languages 
deepl_code=$1
shift
# find the braille tables and names such as:
#   fr-bfu-comp6.utb 'Français, UEB niveau 1'
#   fr-bfu-g2.ctb 'Français, UEB niveau 2'
#   en-ueb-g1.ctb 'British English, UEB grade 1'
#   en-ueb-g2.ctb 'British English, UEB grade 2'
#   de-g1-detailed.ctb 'Deutsch, UEB grade 1'
#   de-g2.ctb 'Deutsch, UEB grade 2'
# note the name should be pre-translated and is shown in the languages menu
declare -a tables
declare -a names
while [ $# -gt 0 ]; do
  tables+=("$1")
  shift
  names+=("$1")
  shift
done

i=0
for table_code in "${tables[@]}"
do
  lower_table_noext=$(echo "${table_code%.*}" | tr '[:upper:]' '[:lower:]')
  locale="${lang_code}.UTF-8@${lower_table_noext}"

  echo "Processing ${locale}"

  table_dir="${locale_dir}/${locale}/LC_MESSAGES"
  if [ ! -d "${table_dir}" ]; then
    mkdir -p "${table_dir}"
  fi

  template_file="${locale_dir}/canute.pot"
  translation_file="${table_dir}/canute_translated_${deepl_code}.po"
  transcribed_file="${table_dir}/canute.po"
  compiled_file="${table_dir}/canute.mo"

  if [ ! -f "${transcribed_file}" ]; then
    # file doesn't exist yet, so create it from template
    msginit -l "${locale}" --no-translator -i "${template_file}" -o "${transcribed_file}"
  else
    # update the file in case there are template changes
    msgmerge --lang="${lang_code}" -U --previous --backup=none "${transcribed_file}" "${template_file}"
  fi
  if [ ! -f "${translation_file}" ] && [ ! -z "${last_translation}" ]; then
    # if we already have a language translation, resue that
    cp "${last_translation}" "${translation_file}"
  fi

  # find any non-braille strings and translate and add them to the translation
  python3 deepl-translate.py -i "${transcribed_file}" -o "${translation_file}" -l "${deepl_code}"

  # use liblouis to transcribe back into original file
  python3 liblouis-transcribe.py -i "${translation_file}" -o "${transcribed_file}" -t "${table_code}" -n "${names[$i]}" $force_transcribe
  last_translation="${translation_file}"

  # compile the .mo from the .po
  pybabel compile -f -D canute -d "${locale_dir}" -l "${locale}" -i "${transcribed_file}" -o "${compiled_file}"

  i=$((i + 1))
done

echo 'Now check changes via git and commit'
