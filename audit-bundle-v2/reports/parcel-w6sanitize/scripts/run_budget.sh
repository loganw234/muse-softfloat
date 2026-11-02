#!/usr/bin/env bash
# usage: run_budget.sh <budget> <logfile> [extra env as KEY=VAL ... via env]
# Runs tools/run.sh in the w6-sanitize worktree, single-stream log.
set -u
BUDGET="$1"; LOG="$2"
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize || exit 9
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
bash tools/run.sh "$BUDGET" > "$LOG" 2>&1
rc=$?
echo "RUN_BUDGET budget=$BUDGET rc=$rc log=$LOG"
tail -5 "$LOG"
exit $rc
