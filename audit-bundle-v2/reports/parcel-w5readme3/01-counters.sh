#!/usr/bin/env bash
# 01-counters.sh - re-derive every README/site number (read-only).
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
ulimit -t 600 2>/dev/null || true
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
export TMPDIR=$PWD/scratch/parcel-w5readme3/tmp
export TMP="$(cygpath -w "$TMPDIR" 2>/dev/null || echo "$TMPDIR")"
export TEMP="$TMP"
mkdir -p scratch/parcel-w5readme3/out scratch/parcel-w5readme3/tmp
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo "python: $MSF_PYTHON ($($MSF_PYTHON --version 2>&1))"
echo "node: $(node --version 2>&1)"
echo "zig: $(scratch/parcel-w5site/zig-x86_64-windows-0.17.0/zig.exe version 2>&1)"
"$MSF_PYTHON" scratch/parcel-w5readme3/counters.py > scratch/parcel-w5readme3/out/counters.txt 2>&1
rc=$?
cat scratch/parcel-w5readme3/out/counters.txt
echo "counters exit: $rc"
exit $rc
