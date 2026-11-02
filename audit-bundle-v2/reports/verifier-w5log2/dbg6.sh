#!/usr/bin/env bash
# dbg6.sh - can cc1 run.
set -u
CC1=/c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/16.1.0/cc1.exe
ls -la "$CC1"
"$CC1" --version > /tmp/cc1.log 2>&1
echo "rc=$?"
cat /tmp/cc1.log | head -5
echo "--- as:"
/c/msys64/mingw64/bin/as.exe --version > /tmp/as.log 2>&1
echo "rc=$?"
head -2 /tmp/as.log
echo "--- mingw32 cc1:"
which gcc
gcc -print-prog-name=cc1
