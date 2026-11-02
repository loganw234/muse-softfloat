#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" scratch/parcel-w4trig/out
gcc -std=c11 -O2 -Wall scratch/parcel-w4trig/cm_zero_probe.c \
  scratch/tier2-oracle-0b/out/cm_sinpi64.o \
  scratch/tier2-oracle-0b/out/cm_cospi64.o \
  -o scratch/parcel-w4trig/out/cm_zero_probe.exe -lm \
  > scratch/parcel-w4trig/out/cm_zero_build.log 2>&1
echo "build rc=$?"; cat scratch/parcel-w4trig/out/cm_zero_build.log
scratch/parcel-w4trig/out/cm_zero_probe.exe \
  > scratch/parcel-w4trig/out/cm_zero.log 2>&1
echo "run rc=$?"
cat scratch/parcel-w4trig/out/cm_zero.log
