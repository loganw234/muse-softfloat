#!/bin/bash
# Probe R: host runner vehicle + unit + full committed-vector verify
# (run.sh smoke components, executed from scratch; the copy's own
# run.sh cannot pass its build_host step - recorded separately).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
cd "$ROOT" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -Wno-error \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c $C/tests/runner.c $C/tests/sha256.c \
  -o $V/tmp/msf_runner.exe > $V/log_runner_build.txt 2>&1
echo "runner build rc=$?"
$V/tmp/msf_runner.exe unit > $V/out/unit.log 2>&1
echo "unit rc=$?"
grep -E 'unit|FAIL|PASS' $V/out/unit.log | head -8
VECS="tests/vectors/encodings-f16.vec tests/vectors/encodings-f32.vec tests/vectors/encodings-f64.vec tests/vectors/copysign.vec tests/vectors/pack64.vec tests/vectors/pack32.vec tests/vectors/pack16.vec tests/vectors/arith-f32.vec tests/vectors/fma-sqrt-f32.vec tests/vectors/conv-int-f32.vec tests/vectors/toint-f32.vec tests/vectors/rint-misc-f32.vec tests/vectors/compare-f32.vec tests/vectors/arith-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/compare-f64.vec tests/vectors/nan-f64.vec tests/vectors/arith-f16.vec tests/vectors/fma-sqrt-f16.vec tests/vectors/conv-int-f16.vec tests/vectors/toint-f16.vec tests/vectors/rint-misc-f16.vec tests/vectors/compare-f16.vec tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec tests/vectors/from-decimal-str.vec tests/vectors/from-hex-str.vec tests/vectors/to-decimal-str.vec tests/vectors/to-hex-str.vec tests/vectors/minmax-f16.vec tests/vectors/minmax-f32.vec tests/vectors/minmax-f64.vec tests/vectors/payload-f16.vec tests/vectors/payload-f32.vec tests/vectors/payload-f64.vec tests/vectors/trig-f16.vec tests/vectors/trig-f32.vec tests/vectors/trig-f64.vec"
cd $C || exit 9
$V/tmp/msf_runner.exe verify $VECS > $V/out/verify_all.log 2>&1
echo "verify rc=$?"
grep -E '^(file|total|VERDICT)' $V/out/verify_all.log | head -50
