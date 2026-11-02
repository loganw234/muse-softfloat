#!/usr/bin/env bash
# verifier-w164 (2b): full Berkeley phase runner; writes one log per phase.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/w1v/tmp
export TMPDIR=$PWD/build/w1v/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64
bash "$SCR/v-berk.sh" "$1" > "$SCR/v-berk-$1.log" 2>&1
echo "phase $1 rc=$?"
