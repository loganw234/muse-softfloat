#!/usr/bin/env bash
# dbg3.sh - trivial compile test.
set -u
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
GCC=/c/msys64/mingw64/bin/gcc.exe
cd "$SCR" || exit 9
printf '#include <stdio.h>\nint main(void){printf("hi\\n");return 0;}\n' > build/hi.c
"$GCC" -std=c11 -O2 build/hi.c -o build/hi.exe > logs/dbg3.log 2>&1
echo "rc=$?"
cat logs/dbg3.log
./build/hi.exe
