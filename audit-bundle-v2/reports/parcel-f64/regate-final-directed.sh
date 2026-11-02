#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
echo "final committed directed verify $(date -Iseconds)"
t0=$(date +%s)
build/smoke/msf_runner.exe verify tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec > build/w1/logs/regate-final-committed-directed.log 2>&1
rc=$?; t1=$(date +%s); echo "rc=$rc seconds=$((t1-t0))"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/regate-final-committed-directed.log
grep '^FAIL' build/w1/logs/regate-final-committed-directed.log | head -5 || true
git -c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64 status --short
exit $rc
