#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
ls -l build/w1/f64_eq---l1.vec
sed 's/msf64_compare_signaling_equal/msf64_compare_quiet_equal/g' build/w1/f64_eq---l1.vec > build/w1/f64_eq-as-quiet.vec
build/smoke/msf_runner.exe verify build/w1/f64_eq-as-quiet.vec > build/w1/logs/f64_eq-as-quiet.verify.log 2>&1
rc=$?
echo "quiet-remap verify rc=$rc"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/f64_eq-as-quiet.verify.log
grep '^FAIL' build/w1/logs/f64_eq-as-quiet.verify.log | head -5 || true
# classify failures in original: all invalid-flag-only on qnan?
grep '^FAIL' build/w1/logs/f64_eq---l1.verify.log | head -3
grep -c '^FAIL' build/w1/logs/f64_eq---l1.verify.log
exit $rc
