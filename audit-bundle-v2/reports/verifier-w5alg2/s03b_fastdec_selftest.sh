#!/usr/bin/env bash
# s03b_fastdec_selftest.sh - prove fastdec == mydecide on 60k pairs.
set -e -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR" scratch/verifier-w5alg2/out
ulimit -v 2097152
OUT=scratch/verifier-w5alg2/out
cat $OUT/s02_f16_hypot_pairs.txt $OUT/s02_f32_hypot_pairs.txt $OUT/s02_f64_hypot_pairs.txt | $MSF_PYTHON scratch/verifier-w5alg2/fastdec.py selftest 2>&1 | tee $OUT/s03b_fastdec_selftest.log
