#!/usr/bin/env bash
# 00_env.sh - environment probe for verifier-w4interval (Git Bash).
set -u
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
export MSF_PYTHON="/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe"
export MSF_HOST_CC="/c/msys64/mingw64/bin/gcc.exe"
echo "bash: $(bash --version | head -1)"
echo "host-cc: $($MSF_HOST_CC -dumpmachine) $($MSF_HOST_CC -dumpversion)"
echo "python: $($MSF_PYTHON --version 2>&1)"
$MSF_PYTHON -c "import numpy; print('numpy:', numpy.__version__)"
echo "copy HEAD: $(git -C "$VROOT/worktrees/verify4-interval" rev-parse --short HEAD)"
echo "copy status:"; git -C "$VROOT/worktrees/verify4-interval" status --short; echo "(end status)"
