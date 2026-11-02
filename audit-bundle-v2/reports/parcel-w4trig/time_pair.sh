#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
START=$(date +%s)
build/trig/trig_exhaustive.exe f32 1065353216 1073741824 > "$O/f32_pair_time.log" 2>&1
echo "pair range rc=$? in $(( $(date +%s) - START ))s"
cat "$O/f32_pair_time.log"
START=$(date +%s)
build/trig/trig_exhaustive.exe f32 0 8388608 > "$O/f32_pair_time0.log" 2>&1
echo "pair range0 rc=$? in $(( $(date +%s) - START ))s"
cat "$O/f32_pair_time0.log"
