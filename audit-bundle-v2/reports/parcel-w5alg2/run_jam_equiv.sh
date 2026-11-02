#!/usr/bin/env bash
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
time "$MSF_PYTHON" "$S/jam_equivalence.py" > "$S/out/jam_equivalence.log" 2>&1
echo "rc=$?"
cat "$S/out/jam_equivalence.log"
