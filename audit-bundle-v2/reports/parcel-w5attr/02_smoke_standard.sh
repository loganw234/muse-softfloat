#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-attr" || exit 9
S="$WS/scratch/parcel-w5attr"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5attr\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
echo "===== smoke ====="
bash tools/run.sh smoke > "$S/out/smoke.log" 2>&1; echo "smoke rc=$?"
tail -5 "$S/out/smoke.log"
grep -E 'VERDICT|control|PASS|FAIL|total' "$S/out/smoke.log" | head -60
echo "===== standard ====="
bash tools/run.sh standard > "$S/out/standard.log" 2>&1; echo "standard rc=$?"
tail -5 "$S/out/standard.log"
grep -E 'VERDICT|PASS|FAIL|total' "$S/out/standard.log" | head -40
