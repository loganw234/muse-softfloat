#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
bash tools/run.sh board
echo "BOARD_RC=$?"
