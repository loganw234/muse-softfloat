#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/w1/directed-check
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
echo "start $(date -Iseconds)"
time $PY tests/gen_vectors_f64.py directed build/w1/directed-check
rc=$?
echo "gen rc=$rc end $(date -Iseconds)"
ls -l build/w1/directed-check
wc -l build/w1/directed-check/*.vec
du -cb build/w1/directed-check/*.vec | tail -1
exit $rc
