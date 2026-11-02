#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
CM=/c/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64
EXE=${1:-build/trig/trig_exhaustive.exe}
TAG=${2:-wc}
for fn in sinpi cospi; do
  sname=sin; [ "$fn" = cospi ] && sname=cos
  START=$(date +%s)
  "$EXE" wc $sname "$CM/$fn/$fn.wc" "$O/${TAG}_${fn}_bits.txt" > "$O/${TAG}_$fn.log" 2>&1
  echo "$fn rc=$? in $(( $(date +%s) - START ))s"
  cat "$O/${TAG}_$fn.log"
done
