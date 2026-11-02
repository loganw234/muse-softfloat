#!/bin/bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
cd "$ROOT" || exit 9
C=worktrees/verify4-trig/tests/vectors/trig-f64.vec
R=scratch/verifier-w4trig/tmp/vecregen/trig-f64.vec
echo "committed bytes/lines:"; wc -c -l $C; tail -c 100 $C | xxd | tail -3
echo "regen bytes/lines:"; wc -c -l $R; tail -c 100 $R | xxd | tail -3
echo "=== committed sin zero lines ==="
grep -n 'sin_pi t[ezpn] 0 ->' $C | head
echo "=== regen sin zero lines ==="
grep -n 'sin_pi t[ezpn] 0 ->' $R | head
