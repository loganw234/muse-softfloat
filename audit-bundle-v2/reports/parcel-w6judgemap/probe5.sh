#!/usr/bin/env bash
# parcel-w6judgemap probe 5: standard at the committed tip + link check inputs
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap
git -c safe.directory=$PWD rev-parse HEAD
git -c safe.directory=$PWD status --short
bash tools/run.sh standard > "$LOG/standard-tip.log" 2>&1; echo "standard-tip rc=$?"
grep -E "VERDICT|budget standard|total 411213|aug_exhaustive" "$LOG/standard-tip.log"
"$MSF_PYTHON" /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap/linkcheck.py README.md > "$LOG/linkcheck-tip.log" 2>&1; echo "linkcheck rc=$?"
tail -2 "$LOG/linkcheck-tip.log"
