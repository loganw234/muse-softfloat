#!/usr/bin/env bash
# usage: bash-run.sh <logfile> <command...>   (runs in worktree)
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32 || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
LOG="$1"; shift
echo "cmd: $*" > "$LOG"
"$@" >> "$LOG" 2>&1
rc=$?
echo "exit: $rc" >> "$LOG"
cat "$LOG"
exit $rc
