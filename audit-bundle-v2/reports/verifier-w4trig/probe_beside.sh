#!/bin/bash
# Probe O2: targeted beside-it - copy passes, mutants fail, same inputs.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
echo "=== B: f16 sin 0x3400 (+0.25, rpos) ==="
echo "-- copy f16_gate.log:"; grep -c 'in=0000000000003400' $V/out/f16_gate.log
echo "-- mutB f16_mutB.log:"; grep 'in=0000000000003400' $V/out/f16_mutB.log | head -4
echo "=== C: f16 sin 0x3556 directed ==="
echo "-- copy f16_gate.log:"; grep -c 'in=0000000000003556' $V/out/f16_gate.log
echo "-- mutC f16_mutC.log:"; grep 'in=0000000000003556' $V/out/f16_mutC.log | head -4
echo "=== A sensitivity: non-sign classes in drop mutant ==="
grep '^MISMATCH' $V/out/wc_sin_drop.log | sed 's/.*fn.*in=/x /' | head -2
