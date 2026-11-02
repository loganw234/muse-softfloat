#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$PWD/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p "$TMPDIR" scratch/parcel-w4trig/out
WT=worktrees/w4-trig
SRC="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c $WT/src/msf_math.c"
gcc -std=c11 -O2 -Wall scratch/parcel-w4trig/debug_harness.c $SRC \
  -o scratch/parcel-w4trig/out/debug_harness.exe -lmpfr -lgmp \
  > scratch/parcel-w4trig/out/dh_build.log 2>&1
echo "build rc=$?"; cat scratch/parcel-w4trig/out/dh_build.log
scratch/parcel-w4trig/out/debug_harness.exe
