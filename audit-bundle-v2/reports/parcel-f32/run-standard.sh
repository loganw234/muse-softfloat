#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32 || exit 9
export TMPDIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/tmp
mkdir -p "$TMPDIR"
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
tools/run.sh standard > /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/standard1.log 2>&1
rc=$?
echo "standard exit: $rc"
tail -15 /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-f32/standard1.log
exit $rc
