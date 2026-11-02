#!/usr/bin/env bash
# budgets.sh - smoke + standard untouched in the worktree.
set -u
cd "$(dirname "$0")/../../worktrees/w4-interval" || exit 9
export MSF_PYTHON="$PWD/../../.venv/Scripts/python.exe"
echo "MSF_PYTHON=$MSF_PYTHON"
bash tools/run.sh smoke 2>&1 | tail -15 || { echo "SMOKE FAIL"; exit 1; }
bash tools/run.sh standard 2>&1 | tail -15 || { echo "STANDARD FAIL"; exit 1; }
echo "BUDGETS OK"
