#!/usr/bin/env bash
# 02_runner_alg.sh - build the copy's own runner and replay its committed alg vectors.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-alg1
OUT=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5alg1/out
mkdir -p "$OUT"
cd "$COPY" || exit 9
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c"
gcc -std=c11 -O2 -ffp-contract=off -Iinclude $SRC tests/runner.c tests/sha256.c \
  -o "$OUT/msf_runner.exe" 2>"$OUT/runner_build.log" || { cat "$OUT/runner_build.log"; exit 1; }
echo "runner built"
"$OUT/msf_runner.exe" verify tests/vectors/alg-f16.vec > "$OUT/verify_alg_f16.log" 2>&1
echo "alg-f16 exit: $?"
tail -5 "$OUT/verify_alg_f16.log"
"$OUT/msf_runner.exe" verify tests/vectors/alg-f32.vec > "$OUT/verify_alg_f32.log" 2>&1
echo "alg-f32 exit: $?"
tail -3 "$OUT/verify_alg_f32.log"
"$OUT/msf_runner.exe" verify tests/vectors/alg-f64.vec > "$OUT/verify_alg_f64.log" 2>&1
echo "alg-f64 exit: $?"
tail -3 "$OUT/verify_alg_f64.log"
