#!/usr/bin/env bash

locale_dir="$PWD/${BASH_SOURCE%/*}"

cd "${locale_dir}/../.."
pybabel extract --add-comments=TRANSLATORS -o ./ui/locale/canute.pot ./ui

cd "${locale_dir}"
./update-language.sh en_GB 'EN-GB' en-ueb-g1.ctb 'English, UEB grade 1' en-ueb-g2.ctb 'English, UEB grade 2'
./update-language.sh de_DE DE de-g1-detailed.ctb 'Deutsch, G1' de-g2.ctb 'Deutsch, G2'
./update-language.sh fr_FR FR fr-bfu-comp6.utb 'Français, G1' fr-bfu-g2.ctb 'Français, G2'
./update-language.sh mn_MN MN mn-MN-g1.utb 'Монгол, G1' mn-MN-g2.ctb 'Монгол, G2'
