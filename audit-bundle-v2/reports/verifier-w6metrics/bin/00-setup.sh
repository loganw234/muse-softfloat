#!/bin/bash
# Setup: create detached duplicate of fe04000 for verifier-w6metrics.
# Never touches worktrees/verify6-metrics.
set -u
ROOT="C:/Users/logan/source/repos/Muse-Softfloat"
MAIN="$ROOT/muse-softfloat"
DUP="$ROOT/scratch/verifier-w6metrics/dup"
export MSF_PYTHON="$ROOT/.venv/Scripts/python.exe"
mkdir -p "$ROOT/scratch/verifier-w6metrics/bin" "$ROOT/scratch/verifier-w6metrics/out"
if [ -d "$DUP" ]; then
  echo "DUP_EXISTS $DUP"
else
  git -C "$MAIN" worktree add --detach "$DUP" fe04000 2>&1
  echo "ADD_RC=$?"
fi
git -C "$DUP" log --oneline -3
git -C "$DUP" status --short | head -5
echo "MSF_PYTHON=$MSF_PYTHON"
"$MSF_PYTHON" --version
