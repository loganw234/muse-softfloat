#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
PY=../../.venv/Scripts/python.exe
echo "start $(date -Iseconds)"
$PY tests/gen_vectors_f64.py sweep build/w1/cross-sweep-seed2.vec 150000 0xC0FFEE > build/w1/logs/cross-sweep2-gen.log 2>&1
echo "gen rc=$?"; cat build/w1/logs/cross-sweep2-gen.log
build/smoke/msf_runner.exe verify build/w1/cross-sweep-seed2.vec > build/w1/logs/cross-sweep2-verify.log 2>&1
rc=$?; echo "verify rc=$rc end $(date -Iseconds)"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/cross-sweep2-verify.log
grep '^FAIL' build/w1/logs/cross-sweep2-verify.log | head -20 || true
exit $rc
