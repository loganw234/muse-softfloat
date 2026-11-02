#!/usr/bin/env bash
# verifier-w4minmax s1: smoke budget in the copy (worktrees/verify4-minmax).
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify4-minmax
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w4minmax
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
mkdir -p "$SCR/tmp" "$SCR/out-smoke"
cd "$COPY" || exit 9
echo "MSF_PYTHON=$MSF_PYTHON"
"$MSF_PYTHON" --version
bash tools/run.sh smoke > "$SCR/out-smoke/smoke.log" 2>&1
rc=$?
tail -25 "$SCR/out-smoke/smoke.log"
echo "SMOKE_RC=$rc"
exit $rc
