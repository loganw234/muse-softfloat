#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 300 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
"$MSF_PYTHON" scratch/parcel-w5readme3/crlfcheck.py > scratch/parcel-w5readme3/out/crlfcheck.log 2>&1
rc=$?
cat scratch/parcel-w5readme3/out/crlfcheck.log
echo "crlf exit: $rc"
exit $rc
