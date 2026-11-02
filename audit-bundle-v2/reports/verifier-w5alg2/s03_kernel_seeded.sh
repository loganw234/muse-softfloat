#!/usr/bin/env bash
# s03_kernel_seeded.sh - kernel floor build vs MY decider on the same
# 60k finite seeded pairs (20k/format x 5 modes = 300,000 decisions).
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
$MSF_PYTHON scratch/verifier-w5alg2/diff_pairs.py kernel-floor 2>&1 | tee $OUT/s03_kernel_floor.log
