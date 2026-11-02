#!/usr/bin/env bash
# s08_jam_kernel.sh - floor build vs JAM build differential.
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
$MSF_PYTHON scratch/verifier-w5alg2/s08_jam_kernel.py 2>&1 | tee $OUT/s08_jam_kernel.log
