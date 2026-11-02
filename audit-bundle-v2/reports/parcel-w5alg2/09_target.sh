#!/usr/bin/env bash
# 09_target.sh - target sizes/stack for msf_alg.o functions.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out/arm" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
arm-none-eabi-gcc --version | head -1
arm-none-eabi-gcc -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb \
  -ffreestanding -fstack-usage -c src/msf_alg.c -o "$S/out/arm/msf_alg.o"
echo "compile rc=$?"
arm-none-eabi-size "$S/out/arm/msf_alg.o"
echo "-- per-function sizes:"
arm-none-eabi-nm --print-size --size-sort "$S/out/arm/msf_alg.o"
echo "-- stack usage:"
cat "$S/out/arm/msf_alg.su"
echo "-- undefined symbols:"
arm-none-eabi-nm -u "$S/out/arm/msf_alg.o"
