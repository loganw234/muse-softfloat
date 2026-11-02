#!/usr/bin/env bash
# 15_run.sh - whole specials table three-way check.
set -u
export PATH=/mingw64/bin:/usr/bin:$PATH
ulimit -v 4194304
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
COPY=worktrees/verify5-alg1
gcc -std=c11 -O2 -ffp-contract=off -I$COPY/include \
  $COPY/src/msf16.c $COPY/src/msf32.c $COPY/src/msf64.c $COPY/src/msf_flags.c \
  $COPY/src/msf_wide.c $COPY/src/msf_roundpack.c $COPY/src/msf_string.c \
  $COPY/src/msf_math.c $COPY/src/msf_alg.c \
  scratch/verifier-w5alg1/11_harness.c \
  -o scratch/verifier-w5alg1/out/vharness.exe || exit 1
/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe -u scratch/verifier-w5alg1/15_specials.py
