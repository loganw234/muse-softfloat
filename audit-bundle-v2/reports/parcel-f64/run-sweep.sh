#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/w1/logs
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
N="${1:-210000}"
OUT="build/w1/cross-sweep-${N}.vec"
echo "sweep start $(date -Iseconds) n=$N"
time $PY tests/gen_vectors_f64.py sweep "$OUT" "$N" 0xF64 > build/w1/logs/cross-sweep-gen.log 2>&1
rc=$?; cat build/w1/logs/cross-sweep-gen.log; echo "gen rc=$rc"
[ $rc -eq 0 ] || exit $rc
ls -l "$OUT"
time build/smoke/msf_runner.exe verify "$OUT" > build/w1/logs/cross-sweep-verify.log 2>&1
rc=$?
echo "verify rc=$rc end $(date -Iseconds)"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/cross-sweep-verify.log
grep '^FAIL' build/w1/logs/cross-sweep-verify.log | head -20 || true
exit $rc
