#!/usr/bin/env bash
# 01_kernel.sh - host + mutant compile of the library with hypot.
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg2" || exit 9
S="$WS/scratch/parcel-w5alg2"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg2\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
CFLAGS="-std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off"

echo "===== build runner (hypot still planned in tables: link-only) ====="
gcc $CFLAGS -DMSF_BUILD_ID='"alg2-kernel"' $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/msf_runner_k.exe" > "$S/out/build_k.log" 2>&1; echo "normal rc=$?"
cat "$S/out/build_k.log"
gcc $CFLAGS -DMSF_BUILD_ID='"alg2-jam"' -DMSF_ALG_TEST_JAM $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/msf_runner_jam.exe" >> "$S/out/build_k.log" 2>&1; echo "jam rc=$?"
gcc $CFLAGS -DMSF_BUILD_ID='"alg2-nosticky"' -DMSF_ALG_TEST_NOSTICKY $SRC tests/runner.c tests/sha256.c \
  -o "$S/out/msf_runner_nosticky.exe" >> "$S/out/build_k.log" 2>&1; echo "nosticky rc=$?"
cat "$S/out/build_k.log"
echo "===== unit ====="
"$S/out/msf_runner_k.exe" unit > "$S/out/unit_k.log" 2>&1; echo "unit rc=$?"
cat "$S/out/unit_k.log"
