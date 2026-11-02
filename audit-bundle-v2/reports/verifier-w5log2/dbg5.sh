#!/usr/bin/env bash
# dbg5.sh - where does mingw64 gcc die.
set -u
G=/c/msys64/mingw64/bin/gcc.exe
echo "--- -v alone:"
"$G" -v > /tmp/gv.log 2>&1
echo "rc=$?"
cat /tmp/gv.log | head -20
echo "--- cc1:"
"$G" -print-prog-name=cc1
echo "--- specs file:"
"$G" -print-file-name=specs
echo "--- try -pipe:"
cd /c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2 || exit 9
"$G" -std=c11 -O2 -pipe build/hi.c -o build/hi_p.exe > logs/dbg5.log 2>&1
echo "rc=$?"
cat logs/dbg5.log | head
