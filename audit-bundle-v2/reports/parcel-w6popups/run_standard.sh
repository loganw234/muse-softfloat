#!/usr/bin/env bash
# Probe (e): tools/run.sh standard must PASS unchanged in the worktree.
set -u
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-popups
export MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
bash tools/run.sh standard
