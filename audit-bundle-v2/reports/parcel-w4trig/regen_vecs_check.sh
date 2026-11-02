#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out/regen-vecs
export MSF_TRIG_DECIDER=$PWD/build/trig/trig_v2.exe
mkdir -p "$O"
$PY tests/gen_vectors_trig.py "$O" > $O.log 2>&1
echo "regen rc=$?"
for f in trig-f16.vec trig-f32.vec trig-f64.vec; do
  cmp tests/vectors/$f "$O/$f" && echo "$f byte-identical"
done
# -Os size of the shipped TU (symbol-scan flags)
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
arm-none-eabi-gcc -std=c11 -Os -Wall -Wextra -Werror -mcpu=cortex-m0plus -mthumb -ffreestanding -c src/msf_math.c -o /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out/msf_math_os.o
echo "arm -Os rc=$?"
arm-none-eabi-size /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out/msf_math_os.o
