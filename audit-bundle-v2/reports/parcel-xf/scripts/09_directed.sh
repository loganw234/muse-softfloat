#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT/worktrees/w2-xf" || exit 9
PY="$ROOT/.venv/Scripts/python.exe"
echo "== directed generation =="
time "$PY" tests/gen_vectors_xf.py directed tests/vectors
echo "directed exit=$?"
echo "== rebuild runner =="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"xf-w2"' \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
  tests/runner.c tests/sha256.c -o build/w2/msf_runner.exe > build/w2/build.log 2>&1
echo "gcc exit=$?"; cat build/w2/build.log
echo "== replay directed =="
./build/w2/msf_runner.exe verify tests/vectors/arith-xf.vec tests/vectors/fma-sqrt-xf.vec \
  tests/vectors/conv-xf.vec tests/vectors/compare-xf.vec tests/vectors/traps-xf.vec \
  > build/w2/verify-directed.log 2>&1
echo "verify exit=$?"
cat build/w2/verify-directed.log
