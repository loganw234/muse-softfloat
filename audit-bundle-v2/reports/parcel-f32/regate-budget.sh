#!/usr/bin/env bash
# usage: regate-budget.sh <smoke|standard> <logfile-basename>
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32 || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/$2
echo "start: $(date '+%Y-%m-%d %H:%M:%S %z') budget=$1" > "$LOG"
SECONDS=0
tools/run.sh "$1" >> "$LOG" 2>&1
rc=$?
echo "end: $(date '+%Y-%m-%d %H:%M:%S %z') wall_seconds=$SECONDS exit=$rc" >> "$LOG"
cat "$LOG"
exit $rc
