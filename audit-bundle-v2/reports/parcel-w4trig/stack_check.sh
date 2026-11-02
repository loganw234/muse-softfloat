#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
arm-none-eabi-gcc -std=c11 -Os -fstack-usage -mcpu=cortex-m0plus -mthumb -ffreestanding \
  -c src/msf_math.c -o "$O/msf_math_su.o" > "$O/su_build.log" 2>&1
echo "rc=$?"
cat src/msf_math.su | sort -k2 -n -r | head -10
rm -f src/msf_math.su
