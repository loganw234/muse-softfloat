#!/usr/bin/env bash
# s08c_f64sim.sh - f64 model-level jam adjudication volume.
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
$MSF_PYTHON scratch/verifier-w5alg2/s08c_f64sim.py 2000000 0x64ad 2>&1 | tee $OUT/s08c_f64sim.log
