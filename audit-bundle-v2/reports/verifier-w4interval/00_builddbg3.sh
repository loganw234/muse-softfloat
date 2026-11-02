#!/usr/bin/env bash
# 00_builddbg3.sh - retry tiny compile with TMPDIR inside workspace.
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
CC="/c/msys64/mingw64/bin/gcc.exe"
mkdir -p "$OUT/build/tmp"
export TMPDIR="$OUT/build/tmp"
export TMP="$OUT/build/tmp"
export TEMP="$OUT/build/tmp"
"$CC" -std=c11 -O2 -Wall -Wextra -Werror -ffp-contract=off "$OUT/build/tiny.c" -o "$OUT/build/tiny.exe"
echo "rc=$?"
"$OUT/build/tiny.exe" && echo "tiny runs"
