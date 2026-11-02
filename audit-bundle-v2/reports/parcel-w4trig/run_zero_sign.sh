#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" scratch/parcel-w4trig/out
gcc --version | head -1
gcc -std=c11 -O2 -Wall scratch/parcel-w4trig/zero_sign_probe.c \
  -o scratch/parcel-w4trig/out/zero_sign_probe.exe -lmpfr -lgmp \
  > scratch/parcel-w4trig/out/zero_sign_build.log 2>&1
echo "build rc=$?"
scratch/parcel-w4trig/out/zero_sign_probe.exe \
  > scratch/parcel-w4trig/out/zero_sign.log 2>&1
echo "run rc=$?"
cat scratch/parcel-w4trig/out/zero_sign.log
