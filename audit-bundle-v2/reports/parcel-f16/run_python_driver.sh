#!/usr/bin/env bash
# usage: run_python_driver.sh <logfile> <script> [args...]
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f16/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
mkdir -p "$TMPDIR"
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
LOG="$1"; shift
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
echo "cmd: $PY $*" > "$LOG"
date >> "$LOG"
"$PY" "$@" >> "$LOG" 2>&1
rc=$?
echo "exit: $rc" >> "$LOG"
date >> "$LOG"
tail -40 "$LOG"
exit $rc
