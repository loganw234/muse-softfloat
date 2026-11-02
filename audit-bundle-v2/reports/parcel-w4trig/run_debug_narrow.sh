#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" scratch/parcel-w4trig/out
gcc -std=c11 -O2 -Wall scratch/parcel-w4trig/debug_narrow.c \
  -o scratch/parcel-w4trig/out/debug_narrow.exe -lmpfr -lgmp
echo "build rc=$?"
scratch/parcel-w4trig/out/debug_narrow.exe
