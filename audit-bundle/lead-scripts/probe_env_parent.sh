#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
export MSF_BOARD_PORT=COM8
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
echo "parent: [$MSF_BOARD_SERIAL]"
bash ../scratch/lead/probe_env_child.sh
echo "--- via tools/run.sh environment (smoke header only, dry) ---"
bash -c 'source board/common.sh; echo "after common: [${MSF_BOARD_SERIAL:-EMPTY}]"'
