#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../../muse-softfloat" || exit 9
export PATH="/c/Program Files/Git/cmd:/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/../scratch/lead/tmp" TMP="$(cygpath -w "$PWD/../scratch/lead/tmp")" TEMP="$TMP"
mkdir -p "$TMPDIR"
export MSF_PYTHON="$PWD/../.venv/Scripts/python.exe"
export MSF_BOARD_SERIAL=E66440A2CB6F5C2B
LOG="$PWD/../scratch/lead/board_augint_interval.log"
bash board/interval_run.sh > "$LOG" 2>&1
rc=$?
echo "board rc=$rc log=$LOG"
grep -E "HOST_SHA256|BOARD_SHA256|SUMMARY|COMPARE|PASS|FAIL|VERDICT" "$LOG" | tail -n 12
exit $rc
