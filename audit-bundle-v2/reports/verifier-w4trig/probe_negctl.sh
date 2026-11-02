#!/bin/bash
# Probe O: negative controls (own mutants; sources in scratch only).
# A: dropped table limb (copy sources + MSF_TRIG_DROP_LIMB) on wc sin.
# B: sin result_sign flip (signfix sources + mutant) on f16.
# C: directed collapse (signfix sources + force te) on f16.
# D: narrowed Ek {100,100,100} (signfix header variant) on wc sin.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
S=$V/signfix
OR=$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
cd "$ROOT" || exit 9
build() { # $1=out $2=srcdir $3=extra flags $4=harness c file
  HARNESS=${4:-$2/tests/trig_exhaustive.c}
  gcc -std=c11 -O2 -Wall -ffp-contract=off -Wno-error \
    -DMSF_TRIG_TEST_COUNTERS $3 \
    -I$2/include -I$2/src $HARNESS \
    $2/src/msf16.c $2/src/msf32.c $2/src/msf64.c $2/src/msf_flags.c \
    $2/src/msf_wide.c $2/src/msf_roundpack.c $2/src/msf_string.c \
    $2/src/msf_math.c -lmpfr -lgmp -o $1 2>/dev/null
  echo "build $1 rc=$?"
}
echo "=== A: drop-limb mutant on wc sin ==="
build $V/tmp/trigx_drop.exe $C "-DMSF_TRIG_DROP_LIMB"
$V/tmp/trigx_drop.exe wc sin $OR/sinpi/sinpi.wc > $V/out/wc_sin_drop.log 2>&1
echo "drop rc=$?"
tail -2 $V/out/wc_sin_drop.log
grep '^MISMATCH' $V/out/wc_sin_drop.log | sed 's/.*in=/in=/' | head -4
echo "=== B: sin signflip mutant on f16 ==="
rm -rf $V/mutB && cp -r $S $V/mutB
sed -i 's/result_sign = d.sign ^ parity ^ r_neg;/result_sign = d.sign ^ parity ^ r_neg ^ 1;/' $V/mutB/src/msf_math.c
grep -n 'r_neg \^ 1' $V/mutB/src/msf_math.c
build $V/tmp/trigx_mutB.exe $V/mutB "" $V/mutB/trig_exhaustive.c
$V/tmp/trigx_mutB.exe f16 > $V/out/f16_mutB.log 2>&1
echo "mutB rc=$?"
tail -2 $V/out/f16_mutB.log
echo "=== C: directed-collapse mutant (force te) on f16 ==="
rm -rf $V/mutC && cp -r $S $V/mutC
sed -i 's|                        rm, &out, &tflags)|                        0, \&out, \&tflags)|' $V/mutC/src/msf_math.c
grep -n '&out, &tflags' $V/mutC/src/msf_math.c
build $V/tmp/trigx_mutC.exe $V/mutC "" $V/mutC/trig_exhaustive.c
$V/tmp/trigx_mutC.exe f16 > $V/out/f16_mutC.log 2>&1
echo "mutC rc=$?"
tail -2 $V/out/f16_mutC.log
echo "=== D: narrowed-Ek mutant {100,100,100} on wc sin ==="
rm -rf $V/mutD && cp -r $S $V/mutD
sed -i 's/MSF_TRIG_EK_EXP\[3\] = { 200, 242, 370 }/MSF_TRIG_EK_EXP[3] = { 100, 100, 100 }/' $V/mutD/src/msf_trig_tables.h
grep -n 'EK_EXP\[3\]' $V/mutD/src/msf_trig_tables.h
build $V/tmp/trigx_mutD.exe $V/mutD "" $V/mutD/trig_exhaustive.c
$V/tmp/trigx_mutD.exe wc sin $OR/sinpi/sinpi.wc > $V/out/wc_sin_mutD.log 2>&1
echo "mutD rc=$?"
tail -3 $V/out/wc_sin_mutD.log
