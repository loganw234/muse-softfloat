#!/usr/bin/env bash
# s00_env.sh - environment record for verifier-w5alg2.
# Run from the repository root under Git Bash.
set -u
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
export MSF_PYTHON="${MSF_PYTHON:-$(pwd)/.venv/Scripts/python.exe}"
export TMPDIR="$(pwd)/scratch/verifier-w5alg2/tmp"
export TMP="$TMPDIR" TEMP="$TMPDIR"
mkdir -p "$TMPDIR"
ulimit -v 4194304
echo "bash: $(bash --version | head -1)"
echo "MSF_PYTHON: $MSF_PYTHON ($($MSF_PYTHON --version 2>&1))"
echo "TMPDIR: $TMPDIR"
echo "gcc: $(gcc -dumpmachine) $(gcc -dumpversion)"
echo "arm gcc: $(arm-none-eabi-gcc --version | head -1)"
echo "mpfr header: $(grep MPFR_VERSION_STRING /c/msys64/mingw64/include/mpfr.h | head -1)"
echo "date: $(date '+%Y-%m-%d %H:%M:%S %z')"
