#!/usr/bin/env bash
# dbg4.sh - find a working C compiler.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
cd "$SCR" || exit 9
printf '#include <stdio.h>\nint main(void){printf("hi\\n");return 0;}\n' > build/hi.c
for CC in /c/msys64/mingw64/bin/gcc.exe /c/msys64/ucrt64/bin/gcc.exe /c/msys64/clang64/bin/clang.exe gcc clang cc; do
  echo "=== $CC ==="
  command -v "$CC" > /dev/null 2>&1 || { echo "not found"; continue; }
  "$CC" --version > logs/cc.log 2>&1
  echo "version rc=$? : $(head -1 logs/cc.log)"
  "$CC" -std=c11 -O2 build/hi.c -o build/hi_t.exe > logs/ccb.log 2>&1
  echo "compile rc=$?"
  head -5 logs/ccb.log
done
