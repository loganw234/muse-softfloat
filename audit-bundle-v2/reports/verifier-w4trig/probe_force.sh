#!/bin/bash
# Probe Q: ARM single-file compile of signfix msf_math.c (same flags as
# board); forced-stage vehicles + wc sin runs; host runner + unit +
# full committed-vector verify.
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ARM="/c/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/14.2 rel1/bin/arm-none-eabi-gcc"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
V=$ROOT/scratch/verifier-w4trig
C=$ROOT/worktrees/verify4-trig
S=$V/signfix
OR=$ROOT/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
cd "$ROOT" || exit 9
echo "=== ARM compile signfix msf_math.c (board flags) ==="
"$ARM" -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb \
  -ffreestanding -I$S/include -I$S/src -c $S/src/msf_math.c \
  -o $V/tmp/msf_math_arm.o 2>&1 | head -5
echo "arm-signfix rc=$?"
echo "=== forced-stage builds (copy sources) ==="
for FS in 1 2; do
gcc -std=c11 -O2 -Wall -ffp-contract=off -Wno-error \
  -DMSF_TRIG_TEST_COUNTERS -DMSF_TRIG_FORCE_START=$FS \
  -I$C/include -I$C/src $C/tests/trig_exhaustive.c \
  $C/src/msf16.c $C/src/msf32.c $C/src/msf64.c $C/src/msf_flags.c \
  $C/src/msf_wide.c $C/src/msf_roundpack.c $C/src/msf_string.c \
  $C/src/msf_math.c -lmpfr -lgmp -o $V/tmp/trigx_fs$FS.exe 2>/dev/null
echo "force_start=$FS build rc=$?"
done
for FS in 1 2; do
$V/tmp/trigx_fs$FS.exe wc sin $OR/sinpi/sinpi.wc > $V/out/wc_sin_fs$FS.log 2>&1
echo "fs$FS rc=$?"
grep -E 'counters|wc sinPi' $V/out/wc_sin_fs$FS.log | tail -2
done
