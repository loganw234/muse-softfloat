#!/usr/bin/env bash
set -u
source "$(dirname "$0")/env.sh"
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
SRC="src/msf16.c src/msf32.c src/msf64.c src/msf_flags.c src/msf_wide.c src/msf_roundpack.c src/msf_string.c src/msf_math.c src/msf_alg.c src/msf_aug.c"
mkdir -p "$WS/scratch/parcel-w5aug/tmp/exh"
gcc -std=c11 -O3 -Wall -Wextra -Werror -ffp-contract=off $SRC tests/aug_exhaustive.c -o "$WS/scratch/parcel-w5aug/tmp/exh/aug_exhaustive.exe" > "$WS/scratch/parcel-w5aug/logs/exh-build.log" 2>&1
echo "build rc=$?"
echo "ulimit -v before: $(ulimit -v)"
ulimit -v 262144 2> "$WS/scratch/parcel-w5aug/logs/ulimit.log"
echo "ulimit set rc=$? now: $(ulimit -v)"
cat "$WS/scratch/parcel-w5aug/logs/ulimit.log"
which time || true
start=$(date +%s)
"$WS/scratch/parcel-w5aug/tmp/exh/aug_exhaustive.exe" pairs add 0 256 > "$WS/scratch/parcel-w5aug/logs/exh-probe.log" 2>&1
rc=$?
echo "probe rc=$rc elapsed=$(( $(date +%s) - start ))s"
cat "$WS/scratch/parcel-w5aug/logs/exh-probe.log"
