#!/usr/bin/env bash
# 01_smoke.sh - run smoke budget in the copy, log to scratch/verifier-w2xf
set -u
cd "/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-xf" || exit 9
export TMPDIR="/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2xf/tmp"
export TMP="$TMPDIR"
export TEMP="$TMPDIR"
mkdir -p "$TMPDIR"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
echo "inner bash: $0"
/usr/bin/bash tools/run.sh smoke 2>&1
echo "EXIT=$?"
