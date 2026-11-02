#!/usr/bin/env bash
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
S="$WS/scratch/parcel-w5alg2"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
"$WS/.venv/Scripts/python.exe" "$S/adjudicate_all.py" gen
"$S/out/alg_decider.exe" decide < "$S/out/adjudicate_all_in.txt" > "$S/out/adjudicate_all_dec.txt"
echo "decide rc=$?"
"$WS/.venv/Scripts/python.exe" "$S/adjudicate_all.py" check
