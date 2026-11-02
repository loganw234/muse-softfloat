#!/usr/bin/env bash
# 11_gates.sh - smoke then standard in the copy (script file, Git Bash,
# MSF_PYTHON pinned to workspace .venv). Never modifies the copy.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$COPY"
echo "=== SMOKE ==="
bash tools/run.sh smoke 2>&1 | tail -30
echo "SMOKE rc=${PIPESTATUS[0]}"
