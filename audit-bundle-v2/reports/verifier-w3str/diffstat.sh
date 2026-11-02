#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR=$R/scratch/verifier-w3str/tmp
export TMP="C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-w3str\tmp"
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
echo "=== diff parent 548a1b9..HEAD stat:"
git -c safe.directory="$R/worktrees/verify3-str" diff --stat 548a1b9..HEAD -- . ':!build' | tail -30
echo
echo "=== implemented.tsv tail:"
tail -15 tables/implemented.tsv
echo
echo "=== status (should be clean):"
git -c safe.directory="$R/worktrees/verify3-str" status --short | head
