#!/usr/bin/env bash
# p1_smoke.sh - run the copy's smoke budget, log to scratch.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-seam
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4seam
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
cd "$COPY" || exit 9
bash tools/run.sh smoke > "$SCR/smoke.log" 2>&1
echo "smoke exit: $?"
tail -5 "$SCR/smoke.log"
