#!/usr/bin/env bash
# 02_kernel.sh - build the MPFR decider against the shipped sources
# and run the first differentials (Git Bash, memory ceiling set).
set -u
ulimit -v 2097152 || echo "ulimit -v unsupported here (recorded)"
WS=/c/Users/logan/source/repos/Muse-Softfloat
cd "$WS/worktrees/w5-alg1" || exit 9
S="$WS/scratch/parcel-w5alg1"
mkdir -p "$S/out" "$S/tmp"
export TMPDIR="$S/tmp"
export TMP='C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w5alg1\tmp'
export TEMP="$TMP"
export MSF_PYTHON="$WS/.venv/Scripts/python.exe"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
echo "===== build alg_decider ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  $SRC tests/alg_decider.c -o "$S/out/alg_decider.exe" -lmpfr -lgmp \
  > "$S/out/build_decider.log" 2>&1
echo "build rc=$?"; cat "$S/out/build_decider.log"
echo "===== f16 exhaustive (65,536 encodings x 5 modes) ====="
time "$S/out/alg_decider.exe" f16 > "$S/out/f16_exhaustive.log" 2>&1
echo "f16 rc=$?"; cat "$S/out/f16_exhaustive.log"
echo "===== seeded f32 (20,000 inputs) ====="
"$S/out/alg_decider.exe" seeded f32 20261028 20000 > "$S/out/seeded_f32_small.log" 2>&1
echo "rc=$?"; cat "$S/out/seeded_f32_small.log"
echo "===== seeded f64 (20,000 inputs) ====="
"$S/out/alg_decider.exe" seeded f64 20261028 20000 > "$S/out/seeded_f64_small.log" 2>&1
echo "rc=$?"; cat "$S/out/seeded_f64_small.log"
echo "===== 02_kernel done ====="
