#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
# representative mixes: normals around 1 (exp field 0x7f), plus subnormal band
for range in "1065353216 1073741824" "0 8388608"; do
  set -- $range
  START=$(date +%s)
  build/trig/trig_exhaustive.exe f32 "$1" "$2" > "$O/f32_time_$1.log" 2>&1
  echo "range $1..$2 rc=$? in $(( $(date +%s) - START ))s"
  cat "$O/f32_time_$1.log"
done
