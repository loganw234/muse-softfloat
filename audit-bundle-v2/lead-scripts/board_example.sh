#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../scratch/lead/tmp" TMP="$(cygpath -w "$PWD/../scratch/lead/tmp")" TEMP="$TMP"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../.venv/Scripts/python.exe"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
LOG="$PWD/../scratch/lead/board_example_pico.log"
bash examples/pico/run_example.sh > "$LOG" 2>&1
rc=$?
echo "board rc=$rc log=$LOG"
tail -n 22 "$LOG"
exit $rc
