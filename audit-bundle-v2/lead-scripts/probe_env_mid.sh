#!/usr/bin/env bash
set -u
echo "level1 before PATH: [${MSF_BOARD_SERIAL:-EMPTY}] bash=$BASH"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
echo "level1 which bash: $(command -v bash)"
bash /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/probe_env_child.sh
echo "--- with explicit prefix ---"
MSF_BOARD_SERIAL=E66440A2CB6F5C2B MSF_BOARD_PORT=COM8 bash /c/Users/logan/source/repos/Muse-Softfloat/scratch/lead/probe_env_child.sh
