#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 600 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
"$MSF_PYTHON" scratch/parcel-w5readme3/counters2.py > scratch/parcel-w5readme3/out/counters2.txt 2>&1
rc=$?
cat scratch/parcel-w5readme3/out/counters2.txt
echo "counters2 exit: $rc"
exit $rc
