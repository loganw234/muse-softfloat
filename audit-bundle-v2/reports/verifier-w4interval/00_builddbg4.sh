#!/usr/bin/env bash
# 00_builddbg4.sh - try -pipe and direct cc1 to isolate failure.
VROOT="/c/Users/logan/source/repos/Muse-Softfloat"
OUT="$VROOT/scratch/verifier-w4interval"
CC="/c/msys64/mingw64/bin/gcc.exe"
mkdir -p "$OUT/build/tmp"
export TMPDIR="$OUT/build/tmp" TMP="$OUT/build/tmp" TEMP="$OUT/build/tmp"
echo "--- attempt 1: -pipe ---"
"$CC" -std=c11 -O2 -pipe "$OUT/build/tiny.c" -o "$OUT/build/tiny1.exe"; echo "rc=$?"
echo "--- attempt 2: cc1 directly ---"
"/c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/16.1.0/cc1.exe" --version; echo "rc=$?"
echo "--- attempt 3: compile only -pipe ---"
"$CC" -std=c11 -O2 -pipe -S "$OUT/build/tiny.c" -o "$OUT/build/tiny.s"; echo "rc=$?"
