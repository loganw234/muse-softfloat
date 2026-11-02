#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32 || exit 9
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
tools/run.sh smoke > /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/smoke1.log 2>&1
rc=$?
echo "smoke exit: $rc"
tail -40 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/smoke1.log
exit $rc
