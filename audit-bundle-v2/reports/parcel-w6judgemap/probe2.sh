#!/usr/bin/env bash
# parcel-w6judgemap probe 2: smoke budget + full demo host (network fetch into gitignored cache)
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-judgemap || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
LOG=/c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6judgemap
bash tools/run.sh smoke > "$LOG/smoke.log" 2>&1; echo "smoke rc=$?"
grep -E "RUN.SH|PASS|FAIL|vectors|budget" "$LOG/smoke.log" | tail -30
bash demo/run_demo.sh host > "$LOG/demo-host.log" 2>&1; echo "demo rc=$?"
tail -40 "$LOG/demo-host.log"
