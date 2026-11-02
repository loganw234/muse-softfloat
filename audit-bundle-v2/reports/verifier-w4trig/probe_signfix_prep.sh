#!/bin/bash
# Probe L: sign-fixed diagnostic sources (scratch copies ONLY; the copy is
# untouched). Fix 1: sin result_sign ^= r_neg. Fix 2: cos half-integer +0.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
cd "$ROOT" || exit 9
rm -rf $V/signfix
mkdir -p $V/signfix
cp -r $C/src $V/signfix/src
cp -r $C/include $V/signfix/include
cp $C/tests/trig_exhaustive.c $V/signfix/
grep -n 'result_sign = d.sign' $V/signfix/src/msf_math.c
grep -n 'return msf_pack_generic(fp, d.sign, 0, msf_u128_from_u64(0u), 0,' $V/signfix/src/msf_math.c
