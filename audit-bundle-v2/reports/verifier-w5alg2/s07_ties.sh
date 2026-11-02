#!/usr/bin/env bash
# s07_ties.sh - tie families, te-vs-ta census, subnormal census.
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
$MSF_PYTHON scratch/verifier-w5alg2/s07_ties.py 2>&1 | tee $OUT/s07_ties.log
