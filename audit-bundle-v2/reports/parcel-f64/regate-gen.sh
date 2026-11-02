#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/w1/logs
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
echo "gen_tables start $(date -Iseconds)"
time $PY tools/gen_tables.py > build/w1/logs/regate-gen-tables.log 2>&1
rc=$?; cat build/w1/logs/regate-gen-tables.log; echo "gen rc=$rc"
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64 status --short
exit $rc
