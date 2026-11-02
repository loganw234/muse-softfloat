#!/usr/bin/env bash
# v04_augpool.sh - build aug harness in scratch, run f16 pool differential.
set -u
ROOT="$PWD"
V="$ROOT/worktrees/verify5-readme3"
B="$ROOT/scratch/verifier-w5readme3/build"
export PATH=/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH
mkdir -p "$B/tmp"
export TMPDIR="$B/tmp" TMP="$B/tmp" TEMP="$B/tmp"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
cd "$V"
gcc -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off $SRC tests/aug_exhaustive.c -o "$B/aug_exhaustive.exe" > "$B/build-aug.log" 2>&1 || { echo "BUILD FAIL"; tail -5 "$B/build-aug.log"; exit 1; }
echo "aug harness built"
"$B/aug_exhaustive.exe" pool > "$B/aug-pool.log" 2>&1
echo "pool exit: $?"
grep -E '^(aug_exhaustive|  kind|VERDICT)' "$B/aug-pool.log"
tail -3 "$B/aug-pool.log"
