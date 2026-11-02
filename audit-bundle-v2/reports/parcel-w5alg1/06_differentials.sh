#!/usr/bin/env bash
# 06_differentials.sh - gate-only differentials at volume:
# binary16 exhaustive (again, on the final tree), seeded
# binary32/64 finite-positive volume. Explicit memory ceiling.
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

echo "===== rebuild decider on final tree ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  $SRC tests/alg_decider.c -o "$S/out/alg_decider.exe" -lmpfr -lgmp \
  > "$S/out/build_decider2.log" 2>&1; echo "build rc=$?"
cat "$S/out/build_decider2.log"

echo "===== binary16 EXHAUSTIVE: all encodings x 5 modes ====="
time "$S/out/alg_decider.exe" f16 > "$S/out/f16_exhaustive_final.log" 2>&1
echo "rc=$?"; cat "$S/out/f16_exhaustive_final.log"

echo "===== binary32 seeded volume: 250,000 inputs x 5 ====="
time "$S/out/alg_decider.exe" seeded f32 20261028 250000 > "$S/out/seeded_f32_final.log" 2>&1
echo "rc=$?"; cat "$S/out/seeded_f32_final.log"

echo "===== binary64 seeded volume: 250,000 inputs x 5 ====="
time "$S/out/alg_decider.exe" seeded f64 20261028 250000 > "$S/out/seeded_f64_final.log" 2>&1
echo "rc=$?"; cat "$S/out/seeded_f64_final.log"

echo "===== binary32/64 second seeds: 100,000 each ====="
"$S/out/alg_decider.exe" seeded f32 777001 100000 > "$S/out/seeded_f32_b.log" 2>&1
echo "f32b rc=$?"; cat "$S/out/seeded_f32_b.log"
"$S/out/alg_decider.exe" seeded f64 777001 100000 > "$S/out/seeded_f64_b.log" 2>&1
echo "f64b rc=$?"; cat "$S/out/seeded_f64_b.log"
echo "===== 06_differentials done ====="
