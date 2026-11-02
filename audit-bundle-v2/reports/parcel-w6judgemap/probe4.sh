#!/usr/bin/env bash
# parcel-w6judgemap probe 4: standard at the final tree (acceptance d)
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap
bash tools/run.sh standard > "$LOG/standard-after.log" 2>&1; echo "standard-after rc=$?"
grep -E "VERDICT|budget standard|total 411213|aug_exhaustive" "$LOG/standard-after.log"
git -c safe.directory=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap status --short
