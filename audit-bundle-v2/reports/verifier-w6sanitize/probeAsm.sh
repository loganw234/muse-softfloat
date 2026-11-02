#!/usr/bin/env bash
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w6sanitize/live/toolcheck || exit 9
gcc -std=c11 -O2 -fsanitize-undefined-trap-on-error -S oadd.c -o oadd-traperr.s 2>&1
echo "--- ud2/ubsan refs in traperr asm ---"
grep -c -i -E "ud2|ubsan" oadd-traperr.s || echo "none found"
gcc -std=c11 -O2 -fsanitize=undefined -S oadd.c -o oadd-ubsan.s 2>&1
echo "--- ud2/ubsan refs in ubsan asm ---"
grep -c -i -E "ud2|ubsan" oadd-ubsan.s || echo "none found"
echo "--- gcc version detail ---"
gcc -v 2>&1 | tail -3
