#!/bin/bash
# Probe L2: build sign-fixed diagnostic vehicle; f16 exhaustive on it.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
S=$V/signfix
cd "$ROOT" || exit 9
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  -DMSF_TRIG_TEST_COUNTERS \
  -I$S/include -I$S/src \
  $S/trig_exhaustive.c \
  $S/src/msf16.c $S/src/msf32.c $S/src/msf64.c $S/src/msf_flags.c \
  $S/src/msf_wide.c $S/src/msf_roundpack.c $S/src/msf_string.c \
  $S/src/msf_math.c \
  -lmpfr -lgmp -o $V/tmp/trigx_fix.exe > $V/log_signfix_build.txt 2>&1
echo "signfix build rc=$? (Werror ON: proves r_neg now used)"
cat $V/log_signfix_build.txt | head -5
$V/tmp/trigx_fix.exe f16 > $V/out/f16_fix.log 2>&1
echo "f16-fix rc=$?"
tail -3 $V/out/f16_fix.log
