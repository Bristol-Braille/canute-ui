#!/usr/bin/env bash

locale_dir="$PWD/${BASH_SOURCE%/*}"

cd "${locale_dir}/../.."
if command -v pybabel >/dev/null 2>&1; then
  pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui
else
  python3 -m babel.messages.frontend extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui
fi

cd "${locale_dir}"
./update-language.sh en_GB 'EN-GB' en-ueb-g1.ctb 'English, UEB Grade 1' en-ueb-g2.ctb 'English, UEB Grade 2'
./update-language.sh de_DE DE de-g1-detailed.ctb 'Deutsch, G1' de-g2.ctb 'Deutsch, G2'
./update-language.sh fr_FR FR fr-bfu-comp6.utb 'Français, G1' fr-bfu-g2.ctb 'Français, G2'
./update-language.sh mn_MN MN mn-MN-g1.utb 'Монгол, G1' mn-MN-g2.ctb 'Монгол, G2'
