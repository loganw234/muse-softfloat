#!/usr/bin/env bash
# 10_standard.sh - standard budget in the copy (regression leg)
set -u
cd "/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-xf" || exit 9
export TMPDIR="/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2xf/tmp"
export TMP="$TMPDIR"
export TEMP="$TMPDIR"
mkdir -p "$TMPDIR"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
/usr/bin/bash tools/run.sh standard 2>&1
echo "EXIT=$?"
