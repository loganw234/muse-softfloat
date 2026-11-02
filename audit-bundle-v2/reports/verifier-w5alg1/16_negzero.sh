#!/usr/bin/env bash
# 16_negzero.sh - record executed-MPFR rSqrt(-0) sign (fenced oracle fact).
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
gcc -std=c11 -O2 scratch/verifier-w5alg1/16_negzero.c \
  -o scratch/verifier-w5alg1/out/negzero.exe -lmpfr -lgmp || exit 1
scratch/verifier-w5alg1/out/negzero.exe
