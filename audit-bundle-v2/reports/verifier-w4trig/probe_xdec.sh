#!/bin/bash
# Probe H: build parcel harness as vehicle (documented -Wno-error vehicle
# build; the -Werror failure itself is recorded separately) and run
# cross-decision: mydecider vs harness `decide` on the sample set.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
C=$ROOT/worktrees/verify4-trig
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
gcc -std=c11 -O2 -Wall -ffp-contract=off -Wno-error \
  -DMSF_TRIG_TEST_COUNTERS \
  -I$C/include -I$C/src \
  $C/tests/trig_exhaustive.c \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c \
  -lmpfr -lgmp -o $V/tmp/trigx.exe > $V/log_trigx_build.txt 2>&1
echo "harness build rc=$?"
head -5 $V/log_trigx_build.txt
$V/tmp/trigx.exe decide < $V/tmp/xdec.in > $V/tmp/xdec.parcel.out 2> $V/log_xdec_parcel.txt
echo "parcel decide rc=$?"
tail -3 $V/log_xdec_parcel.txt
"$PY" $V/mydecider.py $V/tmp/xdec.in $V/tmp/xdec.my.out > $V/log_xdec_my.txt 2>&1
echo "mydecider rc=$?"
cat $V/log_xdec_my.txt
