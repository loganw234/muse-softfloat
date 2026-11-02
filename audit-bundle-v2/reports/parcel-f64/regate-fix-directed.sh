#!/usr/bin/env bash
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1/tmp build/w1/logs
export TMPDIR=$PWD/build/w1/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
echo "== regen directed after second-shape addition $(date -Iseconds) =="
bash ../../scratch/parcel-f64/gen-directed.sh > build/w1/logs/regate-gen-directed2.log 2>&1
rc=$?; echo "gen rc=$rc"; cat build/w1/logs/regate-gen-directed2.log
[ $rc -eq 0 ] || exit $rc
for f in arith-f64 conv-f64 misc-f64 compare-f64 nan-f64; do
  if cmp -s "build/w1/directed-check/$f.vec" "tests/vectors/$f.vec"; then
    echo "IDENTICAL $f.vec"
  else
    echo "DIFFERS $f.vec"
    diff "tests/vectors/$f.vec" "build/w1/directed-check/$f.vec" || true
  fi
done
echo "-- verify directed-check with correct runner --"
build/smoke/msf_runner.exe verify build/w1/directed-check/*.vec > build/w1/logs/regate-directed2-verify.log 2>&1
rc=$?; echo "verify rc=$rc"
grep -E '^(file|prov|total|VERDICT)' build/w1/logs/regate-directed2-verify.log || true
grep '^FAIL' build/w1/logs/regate-directed2-verify.log | head -10 || true
echo "-- verify new arith with wrong-tininess runner (want refusal, 4 fails) --"
# tbefore runner from controls run still exists; rebuild to be current
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_TININESS_AFTER_ROUNDING=0 -DMSF_BUILD_ID='"tininess-before-control"' $SRC tests/runner.c tests/sha256.c -o build/w1/controls/msf_runner_tbefore.exe > build/w1/logs/regate-tbefore-build.log 2>&1
echo "tbefore build rc=$?"
build/w1/controls/msf_runner_tbefore.exe verify build/w1/directed-check/arith-f64.vec > build/w1/logs/regate-tbefore-arith.log 2>&1
rc2=$?; echo "tbefore arith rc=$rc2 (want nonzero)"
grep -E '^(total|VERDICT)' build/w1/logs/regate-tbefore-arith.log || true
grep '^FAIL' build/w1/logs/regate-tbefore-arith.log || true
echo "-- arith line 1824 unchanged check --"
sed -n '1824p' build/w1/directed-check/arith-f64.vec
wc -l tests/gen_vectors_f64.py src/msf64.c
du -cb build/w1/directed-check/*.vec | tail -1
