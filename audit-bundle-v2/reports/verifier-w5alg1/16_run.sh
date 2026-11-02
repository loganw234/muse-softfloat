#!/usr/bin/env bash
# 16_run.sh - build my MPFR cross-decider, run sample, compare.
# Proves the verifier's own decider against an independent oracle.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
VDIR=$ROOT/scratch/verifier-w5alg1
OUT=$VDIR/out
PY=$ROOT/.venv/Scripts/python.exe
mkdir -p "$OUT"
cd "$ROOT" || exit 9
gcc -std=c11 -O2 -ffp-contract=off "$VDIR/16_mpfrx.c" \
  -o "$OUT/mpfrx.exe" -lmpfr -lgmp 2>"$OUT/mpfrx_build.log" \
  || { cat "$OUT/mpfrx_build.log"; exit 1; }
echo "mpfrx built"
$PY -u "$VDIR/16_sample.py"
