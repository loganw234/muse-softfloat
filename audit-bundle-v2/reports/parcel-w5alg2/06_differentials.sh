#!/usr/bin/env bash
# 06_differentials.sh - hypot gate differentials at volume.
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

echo "===== rebuild decider on final tree ====="
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off \
  $SRC tests/alg_decider.c -o "$S/out/alg_decider.exe" -lmpfr -lgmp \
  > "$S/out/build_decider2.log" 2>&1; echo "build rc=$?"
cat "$S/out/build_decider2.log"
D="$S/out/alg_decider.exe"

echo "===== binary16 second-operand sweep vs boundary pool ====="
time "$D" h16pool > "$S/out/h16pool.log" 2>&1; echo "rc=$?"; cat "$S/out/h16pool.log"

echo "===== binary16 counted sampled full sweep: 200,000 pairs ====="
time "$D" h16seed 20261028 200000 > "$S/out/h16seed.log" 2>&1; echo "rc=$?"; cat "$S/out/h16seed.log"

echo "===== binary32 seeded volume: 250,000 finite pairs x5 ====="
time "$D" hseed f32 20261028 250000 > "$S/out/hseed_f32.log" 2>&1; echo "rc=$?"; cat "$S/out/hseed_f32.log"

echo "===== binary64 seeded volume: 250,000 finite pairs x5 ====="
time "$D" hseed f64 20261028 250000 > "$S/out/hseed_f64.log" 2>&1; echo "rc=$?"; cat "$S/out/hseed_f64.log"

echo "===== second seeds: 100,000 each ====="
"$D" hseed f32 777001 100000 > "$S/out/hseed_f32_b.log" 2>&1; echo "f32b rc=$?"; cat "$S/out/hseed_f32_b.log"
"$D" hseed f64 777001 100000 > "$S/out/hseed_f64_b.log" 2>&1; echo "f64b rc=$?"; cat "$S/out/hseed_f64_b.log"
"$D" h16seed 777001 100000 > "$S/out/h16seed_b.log" 2>&1; echo "f16b rc=$?"; cat "$S/out/h16seed_b.log"
echo "===== 06_differentials done ====="
