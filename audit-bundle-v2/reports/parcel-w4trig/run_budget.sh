#!/usr/bin/env bash
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w4-trig
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
O=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w4trig/out
B=${1:-smoke}
START=$(date +%s)
bash tools/run.sh "$B" > "$O/budget_$B.log" 2>&1
echo "$B rc=$? in $(( $(date +%s) - START ))s"
tail -40 "$O/budget_$B.log"
grep -E "trig|inventory|VERDICT|total" "$O/budget_$B.log" | head -20
