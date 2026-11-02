#!/usr/bin/env bash
# verifier-w164 (1b): standard budget + verify committed f64 directed vectors.
set -uo pipefail
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify-f64
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
mkdir -p build/standard/tmp
export TMPDIR=$PWD/build/standard/tmp
export TMP="$(cygpath -w "$TMPDIR")"
export TEMP="$TMP"
export MSF_PYTHON=../../.venv/Scripts/python.exe
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w1f64/v-standard.log
tools/run.sh standard > "$OUT" 2>&1
echo "standard rc=$?"
echo "--- f64 directed verify ---" >> "$OUT"
build/smoke/msf_runner.exe verify tests/vectors/arith-f64.vec tests/vectors/compare-f64.vec tests/vectors/conv-f64.vec tests/vectors/misc-f64.vec tests/vectors/nan-f64.vec >> "$OUT" 2>&1
echo "f64-directed rc=$?" >> "$OUT"
