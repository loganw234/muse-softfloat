#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w4trig\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
EXE=${1:-build/trig/trig_exhaustive.exe}
SEED=${2:-20261027}
N=${3:-2097152}
TAG=${4:-f64seed}
START=$(date +%s)
"$EXE" f64seed "$SEED" "$N" > "$O/$TAG.log" 2>&1
echo "$TAG rc=$? in $(( $(date +%s) - START ))s"
cat "$O/$TAG.log"
