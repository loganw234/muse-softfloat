#!/usr/bin/env bash
# dbg7.sh - retry with mingw64 bin on PATH.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
cd "$SCR" || exit 9
/c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/16.1.0/cc1.exe --version 2>&1 | head -2
echo "cc1 rc=$?"
gcc -dumpmachine
gcc --version | head -1
printf '#include <stdio.h>\nint main(void){printf("hi\\n");return 0;}\n' > build/hi.c
gcc -std=c11 -O2 build/hi.c -o build/hi64.exe
echo "compile rc=$?"
./build/hi64.exe
