#!/bin/bash
# Probe S: signfix runner + trig-vector replay (expect exactly the 1
# stale line); type scan (copy); symbol scan (copy ARM objects).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
S=$V/signfix
cd "$ROOT" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -Wno-error \
  $S/src/msf16.c $S/src/msf32.c $S/src/msf64.c $S/src/msf_flags.c \
  $S/src/msf_wide.c $S/src/msf_roundpack.c $S/src/msf_string.c \
  $S/src/msf_math.c $C/tests/runner.c $C/tests/sha256.c \
  -o $V/tmp/msf_runner_fix.exe 2>/dev/null
echo "fix runner build rc=$?"
cd $C || exit 9
$V/tmp/msf_runner_fix.exe verify tests/vectors/trig-f16.vec tests/vectors/trig-f32.vec tests/vectors/trig-f64.vec > $V/out/verify_trig_fix.log 2>&1
echo "fix trig verify rc=$?"
grep -E '^(file|total|VERDICT)' $V/out/verify_trig_fix.log
grep '^FAIL' $V/out/verify_trig_fix.log | head -5
cd "$ROOT" || exit 9
echo "=== type scan (copy src+include) ==="
if grep -rnwE 'float|double' $C/src $C/include > $V/out/type_scan.txt 2>&1; then
  echo "TYPE SCAN DIRTY:"; head -5 $V/out/type_scan.txt
else
  echo "type scan: clean"
fi
echo "=== symbol scan (copy ARM objects from fwbuild) ==="
ls $V/fwbuild/CMakeFiles/msf_core.dir/__/worktrees/verify4-trig/src/ 2>/dev/null
find $V/fwbuild -name 'msf_*.obj' | head -12
