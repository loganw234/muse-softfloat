#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
echo "start $(date -Iseconds)"
build/smoke/msf_runner.exe verify build/w1/directed-check/*.vec > build/w1/directed-verify.log 2>&1
rc=$?
echo "verify rc=$rc end $(date -Iseconds)"
grep -E '^(file|prov|total|VERDICT)' build/w1/directed-verify.log
echo "--- failures (first 80) ---"
grep '^FAIL' build/w1/directed-verify.log | head -80 || true
grep -c '^FAIL' build/w1/directed-verify.log || true
exit $rc
