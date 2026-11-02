#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
cd "$ROOT/worktrees/w2-xf" || exit 9
"$ROOT/.venv/Scripts/python.exe" "$ROOT/scratch/parcel-xf/scripts/16_controls.py"
echo "controls gen exit=$?"
R=./build/w2/msf_runner.exe
$R verify build/w2/controls/flip-result-bit.vec > build/w2/controls/flip-result-bit.log 2>&1
rc1=$?
echo "control flip-result-bit runner exit=$rc1 (want nonzero)"
grep -E '^(FAIL|total|VERDICT)' build/w2/controls/flip-result-bit.log | head -4
$R verify build/w2/controls/trap-flip.vec > build/w2/controls/trap-flip.log 2>&1
rc2=$?
echo "control trap-flip runner exit=$rc2 (want nonzero)"
grep -E '^(FAIL|total|VERDICT)' build/w2/controls/trap-flip.log | head -4
echo "control planned-only: see smoke log line:"
grep "planned-only" "$ROOT/scratch/parcel-xf/logs/11_smoke_full.log"
if [ $rc1 -ne 0 ] && [ $rc2 -ne 0 ]; then echo "CONTROLS: both refused as required"; else echo "CONTROLS: NOT REFUSED - FAIL"; fi
