#!/usr/bin/env bash
# s04_pool_f16.sh - binary16 pool sweep gate (6,553,600 decisions).
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
$MSF_PYTHON scratch/verifier-w5alg2/s04_pool_f16.py 2>&1 | tee $OUT/s04_pool_f16.log
