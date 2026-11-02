#!/usr/bin/env bash
# 00_builddbg2.sh - capture gcc stderr visibly.
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
CC="/c/msys64/mingw64/bin/gcc.exe"
echo "--- verbose tiny compile ---"
"$CC" -v -std=c11 -O2 "$OUT/build/tiny.c" -o "$OUT/build/tiny.exe"
echo "rc=$?"
