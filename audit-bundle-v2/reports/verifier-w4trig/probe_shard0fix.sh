#!/bin/bash
# Probe M: copy shard-0 (expect early abort at 100k), signfix wc gates,
# forced-stage vehicle builds.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
S=$V/signfix
OR=$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
cd "$ROOT" || exit 9
echo "=== copy f32 shard 0 [0, 2^26) ==="
time $V/tmp/trigx.exe f32 0 67108864 > $V/out/f32sh0_copy.log 2>&1
echo "shard0-copy rc=$?"
tail -3 $V/out/f32sh0_copy.log
echo "=== signfix wc sin+cos ==="
$V/tmp/trigx_fix.exe wc sin $OR/sinpi/sinpi.wc > $V/out/wc_sin_fix.log 2>&1
echo "wc-sin-fix rc=$?"
tail -2 $V/out/wc_sin_fix.log
$V/tmp/trigx_fix.exe wc cos $OR/cospi/cospi.wc > $V/out/wc_cos_fix.log 2>&1
echo "wc-cos-fix rc=$?"
tail -2 $V/out/wc_cos_fix.log
echo "=== forced-stage vehicle builds (copy sources) ==="
for FS in 1 2; do
gcc -std=c11 -O2 -Wall -ffp-contract=off -Wno-error \
  -DMSF_TRIG_TEST_COUNTERS -DMSF_TRIG_FORCE_START=$FS \
  -I$C/include -I$C/src $C/tests/trig_exhaustive.c \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c \
  -lmpfr -lgmp -o $V/tmp/trigx_fs$FS.exe 2>/dev/null
echo "force_start=$FS build rc=$?"
done
