#!/usr/bin/env bash
set -u
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-demo" || exit 9
export MSF_PYTHON=$WS/.venv/Scripts/python.exe
time bash tools/run.sh smoke
echo "SMOKE_EXIT=$?"
