#!/usr/bin/env bash
set -uo pipefail
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
export TMPDIR="$ROOT/scratch/parcel-xf/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-xf\tmp'
export TEMP="$TMP"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$ROOT/worktrees/w2-xf" || exit 9
mkdir -p build/w2
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off -DMSF_BUILD_ID='"xf-check"' \
  src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c \
  tests/runner.c tests/sha256.c -o build/w2/msf_runner.exe > build/w2/build.log 2>&1
rc=$?
echo "gcc exit=$rc"
cat build/w2/build.log
if [ $rc -eq 0 ]; then ./build/w2/msf_runner.exe unit; echo "unit exit=$?"; fi
