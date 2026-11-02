#!/usr/bin/env bash
# 12_standard.sh - standard gate in the copy (script file, Git Bash,
# MSF_PYTHON pinned to workspace .venv). Never modifies the copy.
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
COPY="$VROOT/worktrees/verify4-interval"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
cd "$COPY"
echo "=== STANDARD ==="
bash tools/run.sh standard 2>&1 | tail -15
echo "STANDARD rc=${PIPESTATUS[0]}"
