#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
$ROOT/.venv/Scripts/python.exe "$S/threshold-sweep.py"
build/str/msf_runner.exe verify "$S/bulk/threshold.vec" > "$S/threshold.log" 2>&1
echo "threshold rc=$?"
grep -E '^(file|total|VERDICT)' "$S/threshold.log"
grep '^FAIL' "$S/threshold.log" | head -10
