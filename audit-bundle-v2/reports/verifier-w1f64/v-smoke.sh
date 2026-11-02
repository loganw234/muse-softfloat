#!/usr/bin/env bash
# verifier-w164 (1): budgets smoke + standard in the verify-f64 copy.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/smoke/tmp build/standard/tmp
export TMPDIR=$PWD/build/smoke/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export MSF_PYTHON=../../.venv/Scripts/python.exe
echo "verifier-w164 smoke start $(date -Iseconds)"
echo "machine: under third-party load (no rate claims)"
tools/run.sh smoke > /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64/v-smoke.log 2>&1
echo "smoke rc=$?"
