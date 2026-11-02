#!/usr/bin/env bash
set -u
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
W=$ROOT/worktrees/w3-str
S=$ROOT/scratch/parcel-str
export TMPDIR=$S/tmp
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str\tmp'
export TEMP="$TMP"
cd "$W" || exit 9
$ROOT/.venv/Scripts/python.exe "$S/longstring-sweep.py"
build/str/msf_runner.exe verify "$S/bulk/longstring.vec" > "$S/longstring.log" 2>&1
echo "rc=$?"
grep -E '^(file|total|VERDICT)' "$S/longstring.log"
grep '^FAIL' "$S/longstring.log" | head -5 | cut -c1-220
