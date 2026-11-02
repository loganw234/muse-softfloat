#!/usr/bin/env bash
# s_standard.sh - run standard budget in the verify copy
set -u
cd "C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16" || exit 9
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_HOST_CC=gcc
export MSF_PYTHON="C:/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
bash tools/run.sh standard > "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/standard.log" 2>&1
echo "exit=$?" > "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/standard.exit"
