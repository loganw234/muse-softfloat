#!/usr/bin/env bash
# standard.sh - run from worktree root.
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
bash tools/run.sh standard > "$WS/scratch/parcel-w6augint/standard.log" 2>&1
rc=$?
tail -5 "$WS/scratch/parcel-w6augint/standard.log"
grep -E '^(budget|negative controls|inventory:|VERDICT|total)' "$WS/scratch/parcel-w6augint/standard.log" | tail -12
echo "standard rc=$rc"
exit $rc
