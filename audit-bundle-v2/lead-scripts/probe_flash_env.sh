#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export MSF_BOARD_SERIAL=e66440a2cb6f5c2b
echo "before source: [$MSF_BOARD_SERIAL]"
source board/common.sh
echo "after source: [${MSF_BOARD_SERIAL:-EMPTY}]"
declare -f flash_uf2 | grep -A3 -B2 'ser_arg\|PICOTOOL.*load'
