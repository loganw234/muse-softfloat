#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -c src/msf_math.c -o $O/msf_math.o > $O/cc_host.log 2>&1
echo "host rc=$?"; cat $O/cc_host.log
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_TRIG_TEST_COUNTERS -c src/msf_math.c -o $O/msf_math_test.o >> $O/cc_host.log 2>&1
echo "host-test rc=$?"; cat $O/cc_host.log
if command -v arm-none-eabi-gcc >/dev/null 2>&1; then
  arm-none-eabi-gcc -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -c src/msf_math.c -o $O/msf_math_arm.o > $O/cc_arm.log 2>&1
  echo "arm rc=$?"; cat $O/cc_arm.log
  arm-none-eabi-nm -u $O/msf_math_arm.o | sort -u > $O/cc_arm_undef.txt
  echo "arm undefined:"; cat $O/cc_arm_undef.txt
  arm-none-eabi-size $O/msf_math_arm.o
else
  echo "arm compiler not on PATH here (run.sh adds it if present)"
fi
